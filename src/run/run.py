import os
import resource
import re
import time
from multiprocessing import Pool, TimeoutError

from tqdm import tqdm
import dlplan
import tarski.fstrips

import src.sketch_generation.generation
import src.transition_system as ts
import src.file_manager.names as names
from src.logics.rules import Sketch
from src.sketch_generation.generation import construct_feature_generator
from src.file_manager.cashing import cache_to_file
from src.sketch_verification.feature_instance import FeatureInstance
from src.sketch_verification.verify import verify_sketch
from src.sketch_verification.laws import law1, law2, impl_law

from src.utils.timer import timer
import warnings

warnings.filterwarnings("ignore")


def sort_files(fs: list[str]):
    """
    Sort instance files such that numbers are increasing
    e.g. p-3-5, p-3-10, p-10-5, p-10-10, ...
    Credits to Adam Vandervorst
    :param fs: a list of file names to sort
    :return: a sorted list of file names
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(fs, key=alphanum_key)


def cache_all_transition_systems(domain_file: str, instance_files: list[str]) -> None:
    """
    Build and save all transition systems from a list of instances from the same domain to files
    Transition systems are saved because the 'tarski_to_transition_system' method is cached
    :param domain_file: PDDL file that contains a planning domain description
    :param instance_files: PDDL files that contain instances of the planning domain
    :return:
    """
    print("Building transition systems and reading states")
    for inst_f in tqdm(instance_files):
        instance: tarski.fstrips.Problem = ts.tarski.load_instance(domain_file, directory + inst_f)
        instance.name = inst_f.removesuffix(".pddl")
        ts.tarski.tarski_to_transition_system(instance)
    print("Done with transition systems")


def run_on_multiple_instances(directory: str, domain_file: str, instance_files: list[str], generator_params: list[int],
                              max_features, max_rules, time_limit=None) -> None:
    """
    Generate and verify sketches for a planning domain given domain instances. All working sketches are cached to a
    file. The sketches can be found in:
    "generated/'domain_name'/'generator_params'_'max_features'/rules_'max_rules'.json"
    Note: to model-check a sketch over one instance, a time-limit of 5 minutes is used. If the time limit is passed,
    the sketch is labeled as "timed-out" and the algorithm moves on to the next candidate sketch.
    :param directory: The directory in which all domain and instance files can be found
    :param domain_file: The name of the PDDL file defining the domain
    :param instance_files: The names of PDDL files that specify instances of the domain in order of increasing size.
    :param generator_params: The parameters to use when generating features using the DLPlan library, these parameters
        are in order:
            concept_complexity_limit: int = 9,
            role_complexity_limit: int = 9,
            boolean_complexity_limit: int = 9,
            count_numerical_complexity_limit: int = 9,
            distance_numerical_complexity_limit: int = 9,
            time_limit: int = 3600,
            feature_limit: int = 10000
    :param max_features: The maximum amount of features a sketch can use
    :param max_rules: The number of rules a sketch can use
    :param time_limit: Time limit in seconds for generating and verifying sketches. The time to built transition systems
                        is not taken into account here. The timer starts after all systems are built.
    :return: Nothing, good sketches are saved to a file
    """
    assert (len(generator_params) == 7)
    domain = ts.tarski.load_domain(domain_file)
    dl_vocab = ts.conversions.dlvocab_from_tarski(domain.language)
    domain_name = domain.domain_name
    all_states = []
    systems = []

    print("Building transition systems and reading states")
    for inst_f in tqdm(instance_files):
        instance: tarski.fstrips.Problem = ts.tarski.load_instance(domain_file, directory + inst_f)
        instance.name = inst_f.removesuffix(".pddl")
        transition_system = ts.tarski.tarski_to_transition_system(instance)
        dlinstance = ts.conversions.dlinstance_from_tarski(domain, instance)
        dlstates = [ts.dlplan.dlstate_from_state(s, dlinstance) for s in transition_system.states]
        systems.append(transition_system)
        all_states.append(dlstates)
    print("Done with transition systems")

    factory = dlplan.core.SyntacticElementFactory(dl_vocab)
    generator = construct_feature_generator()

    # create a cached method that generates features such that results can be reused if the same features were already
    # generated in the past
    cached_generate = cache_to_file(f"../../cache/{domain_name}/features/", lambda x: x,
                                    lambda x: x, names.feature_file)(
        timer(f"../../cache/{domain_name}/timers/features/", names.feature_file)(generator.generate))
    params = generator_params
    string_features: list[str] = list(filter(lambda x: x.startswith("n_") or x.startswith("b_"),
                                             cached_generate(factory, [s for states in all_states for s in states],
                                                             *params)))
    # remove features that are always the same for each state in an instance, and for all instances
    filtered_features = [f for f in string_features if f not in ["b_empty(c_top)",
                                                                 "b_empty(c_bot)",
                                                                 "n_count(c_top)",
                                                                 "n_count(c_bot)"]]

    bools = [f for f in filtered_features if f.startswith("b_")]
    nums = [f for f in filtered_features if f.startswith("n_")]

    @cache_to_file(f"../../cache/{domain_name}/features/{'_'.join(map(str, params))}/", lambda x: x, lambda x: x,
                   lambda x, y, z: f"{z}.json")
    @timer(f"../../cache/{domain_name}/timers/features/{'_'.join(map(str, params))}/", lambda x, y, z: f"{z}.json")
    def calculate_feature_vals(sts: list[dlplan.core.State], fs: list[str], filename) -> dict:
        """Calculate the values of features in states"""
        # We need to recreate the element factory using one of the states of an instance. We don't know why but using
        # the factory defined previously results in errors.
        fact = dlplan.core.SyntacticElementFactory(sts[0].get_instance_info().get_vocabulary_info())
        boolean_features = [fact.parse_boolean(f) for f in fs if f.startswith("b_")]
        numerical_features = [fact.parse_numerical(f) for f in fs if f.startswith("n_")]

        return {f.compute_repr(): [f.evaluate(s) for s in sts] for f in numerical_features + boolean_features}

    @cache_to_file(f"../../generated/{domain_name}/{'_'.join(map(str, generator_params))}_{max_features}/",
                   serializer=lambda ws_n: dict(working=[ws.serialize() for ws in ws_n[0]],
                                                timed_out=[(s.serialize(), n, i) for s, n, i in ws_n[1]],
                                                number_tested=ws_n[2], stable=ws_n[3],
                                                instance_files=ws_n[4], timings=ws_n[5]),
                   deserializer=lambda d: ([Sketch.deserialize(r) for r in d["working"]],
                                           [(Sketch.deserialize(r), n, i) for r, n, i in d['timed_out']],
                                           d["number_tested"], d["stable"], d["instance_files"], d["timings"]),
                   namer=lambda n, *_: f'rules_{n}.json')
    @timer(f"../../generated/{domain_name}/timers/{'_'.join(map(str, generator_params))}_{max_features}/",
           lambda n, *_: f'rules_{n}.json')
    def with_n_rules(n, past_sketches, time_limit_s=None):
        """Generate candicate sketches and verify them. This part is put in a separate method such that we can wrap a
        timer around it"""
        changes = set()
        timed_out_sketches = list[(Sketch, int, str)]()
        candidate_sketches = src.sketch_generation.generation.generate_sketches(bools, nums, n, max_features)
        # filtered_candidate_sketches = filter(lambda s2: not (any(s2.simplify().contains_sketch(s1.simplify()) for s1 in past_sketches)),
        #                                     candidate_sketches)
        working_sketches = []
        sketch_number = 0
        timings = []

        start_time = time.monotonic_ns()
        for sketch in tqdm(candidate_sketches):
            sketch = sketch.simplify()
            # TODO if a simplified sketch is equal to a previous sketch, skip it.
            # TODO another way to solve this is to adjust the generation method to never generate duplicate sketches
            # TODO by e.g. not using the "Any" options such that simplification is not necessary
            # if any(sketch.rules == ws.rules for ws in working_sketches):
            #    print("got the case")  # this occurs sometimes, but not enough to be significant
            #    continue
            sketch_number += 1
            verified = True
            # (time, accepted)
            timings_sketch = list[(float, int)]()

            for e, i in enumerate(instance_files):
                feature_vals = calculate_feature_vals(all_states[e], filtered_features, i.removesuffix(".pddl"))
                feature_instance = FeatureInstance(systems[e].graph, systems[e].init, systems[e].goals, feature_vals)

                aresult = p.apply_async(func=verify_sketch, args=(sketch, feature_instance, [law1, law2, impl_law]))

                starttime = time.monotonic_ns()
                try:
                    verified = aresult.get(600)
                    # verified = verify_sketch(sketch, feature_instance, [law1, law2, impl_law])
                    endtime = time.monotonic_ns()
                except TimeoutError:
                    print("time out!", sketch_number, i)
                    endtime = time.monotonic_ns()
                    timed_out_sketches.append((sketch, e, i))
                    timings_sketch.append((endtime - starttime, -1))
                    break

                if not verified:
                    changes.add((e, i))
                    timings_sketch.append((endtime - starttime, 0))
                    break
                timings_sketch.append((endtime - starttime, 1))
            if verified:
                working_sketches.append(sketch)
            timings.append(timings_sketch)
            if time_limit_s and (time.monotonic_ns() - start_time) >= time_limit_s * 1_000_000_000:
                break
        return working_sketches, timed_out_sketches, sketch_number, list(changes), instance_files, timings

    with Pool(processes=1) as p:
        past_sketches = []
        # for n_rules in range(1, max_rules + 1):
        working_sketches, *_ = with_n_rules(max_rules, past_sketches, time_limit)
        # past_sketches.extend(working_sketches)

    print("RESOURCE USAGE", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__ == '__main__':
    domain_name = "blocks_4_on"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files = sort_files(files)
    instance_files = list(filter(lambda x: x.startswith('p-'), files))
    # instance_files.remove("domain.pddl")
    # instance_files.remove("domain-with-fix.pddl")
    # instance_files.remove("README")
    """concept_complexity_limit: int = 9, role_complexity_limit: int = 9, boolean_complexity_limit: int = 9, count_numerical_complexity_limit: int = 9, distance_numerical_complexity_limit: int = 9, time_limit: int = 3600, feature_limit: int = 10000) -> List[str] """
    # final
    # generator_params = [8, 8, 8, 8, 8, 3600, 10000]
    # max_features = 4
    # max_rules = 6

    # blocks clear Drexler params
    complexity = 4
    generator_params = [complexity, complexity, complexity, complexity, complexity, 180, 10000]
    max_features = 1
    max_rules = 1

    filename = f"all_instances_{'_'.join(map(str, generator_params))}_{str(max_rules)}_{str(max_features)}.json"


    @timer(f"../../generated/{domain_name}/timers/", lambda: filename)
    def write_all():
        file_dir = f"../../generated/{domain_name}/"
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        run_on_multiple_instances(directory, domain_file, instance_files, generator_params, max_features, max_rules)


    write_all()
