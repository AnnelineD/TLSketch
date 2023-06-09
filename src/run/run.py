import json
import os
import resource
import time

import tarski.fstrips

import src.sketch_generation.generation
import src.transition_system as ts
import dlplan

import src.file_manager.names as names
from src.logics.conditions_effects import Feature
from src.logics.rules import Sketch
from src.sketch_generation.generation import construct_feature_generator
from src.file_manager.cashing import cache_to_file
from src.sketch_verification.feature_instance import FeatureInstance
from src.sketch_verification.verify import verify_sketch
from src.sketch_verification.laws import law1, law2, law3, simple_law, impl_law, exists_impl_law
from tqdm import tqdm
import src.file_manager as fm
from src.transition_system.transition_system import TransitionSystem

from src.utils.timer import timer
import warnings
warnings.filterwarnings("ignore")
import re

def sort_files(fs: list[str]):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(fs, key=alphanum_key)


def run():
    domain = ts.tarski.load_domain("../../domains/miconic/domain.pddl")

    instance = ts.tarski.load_instance("../../domains/miconic/domain.pddl", "../../domains/miconic/p-2-2-2.pddl")
    transition_system = ts.tarski.tarski_to_transition_system(instance)
    dlinstance = ts.conversions.dlinstance_from_tarski(domain, instance)
    dlstates = [ts.dlplan.dlstate_from_state(s, dlinstance) for s in transition_system.states]

    factory = dlplan.SyntacticElementFactory(dlinstance.get_vocabulary_info())
    generator = construct_feature_generator()

    cached_generate = cache_to_file(f"../../cache/{instance.domain_name}/features/", lambda x: x, lambda x: x, names.feature_file)(generator.generate)
    params = [5, 5, 10, 10, 10, 180, 100000, 1]
    string_features: list[str] = list(filter(lambda x: x.startswith("n_") or x.startswith("b_"), cached_generate(factory, *params, dlstates)))      # TODO check these parameters
    bools = [f for f in string_features if f.startswith("b_")]
    nums = [f for f in string_features if f.startswith("n_")]

    def named_feature_vals(dlstates, string_features, factory) -> str:
        return f"{'_'.join([c.name for c in instance.language.constants()])}_{instance.goal.__repr__().replace(' ', '')}.json"

    @cache_to_file(f"../../cache/{instance.domain_name}/features/{'_'.join(map(str, params))}/", lambda x: x, lambda x: x, named_feature_vals)
    def calculate_feature_vals(sts: list[dlplan.State], fs: list[str], fact) -> dict:
        boolean_features = [fact.parse_boolean(f) for f in fs if f.startswith("b_")]
        numerical_features = [fact.parse_numerical(f) for f in fs if f.startswith("n_")]

        return {f.compute_repr(): [f.evaluate(s) for s in sts] for f in numerical_features + boolean_features}

    feature_vals = calculate_feature_vals(dlstates, string_features, factory)
    candidate_sketches = src.sketch_generation.generation.generate_sketches(bools, nums, 1)
    feature_instance = FeatureInstance(transition_system.graph, transition_system.init, transition_system.goals, feature_vals)
    print("got sketch generator")
    for s in candidate_sketches:
        the_one_sketch = next(candidate_sketches)
        checked = verify_sketch(the_one_sketch, feature_instance, [law1, law2, law3])
        print(checked)
        if checked:
            print(the_one_sketch)


def cache_all_transition_systems(domain_file: str, instance_files: list[str]):
    print("Building transition systems and reading states")
    for inst_f in tqdm(instance_files):
        instance: tarski.fstrips.Problem = ts.tarski.load_instance(domain_file, directory + inst_f)
        instance.name = inst_f.removesuffix(".pddl")
        ts.tarski.tarski_to_transition_system(instance)
    print("Done with transition systems")


def run_on_multiple_instances(domain_file: str, instance_files: list[str], generator_params: list[int], max_features, max_rules):
    assert(len(generator_params) == 7)
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

    factory = dlplan.SyntacticElementFactory(dl_vocab)
    generator = construct_feature_generator()

    cached_generate = cache_to_file(f"../../cache/{domain_name}/features/", lambda x: x,
                                    lambda x: x, names.feature_file)(timer(f"../../cache/timers{domain_name}/features/", names.feature_file)(generator.generate))
    params = generator_params
    string_features: list[str] = list(filter(lambda x: x.startswith("n_") or x.startswith("b_"), cached_generate(factory, [s for states in all_states for s in states], *params)))      # TODO check these parameters
    filtered_features = [f for f in string_features if f not in ["c_bot", "c_top", "b_empty(c_top)",
                                                                 "b_empty(c_bot)",
                                                                 "n_count(c_top)",
                                                                 "n_count(c_bot)"]]

    bools = [f for f in filtered_features if f.startswith("b_")]
    nums = [f for f in filtered_features if f.startswith("n_")]

    @cache_to_file(f"../../cache/{domain_name}/features/{'_'.join(map(str, params))}/", lambda x: x, lambda x: x, lambda x, y, z: f"{z}.json")
    @timer(f"../../cache/timers/{domain_name}/features/{'_'.join(map(str, params))}/", lambda x, y, z: f"{z}.json")
    def calculate_feature_vals(sts: list[dlplan.State], fs: list[str], filename) -> dict:
        fact = dlplan.SyntacticElementFactory(sts[0].get_instance_info().get_vocabulary_info()) # TODO why doesn't it work with the given factory?
        boolean_features = [fact.parse_boolean(f) for f in fs if f.startswith("b_")]
        numerical_features = [fact.parse_numerical(f) for f in fs if f.startswith("n_")]

        return {f.compute_repr(): [f.evaluate(s) for s in sts] for f in numerical_features + boolean_features}

    @cache_to_file(f"../../generated/{domain_name}/{'_'.join(map(str, generator_params))}_{max_features}/",
                   serializer=lambda ws_n: dict(working=[ws.serialize() for ws in ws_n[0]], number_tested=ws_n[1], stable=ws_n[2]),
                   deserializer=lambda d: ([Sketch.deserialize(r) for r in d["working"]], d["number_tested"], d["stable"]),
                   namer=lambda n, _: f'rules_{n}.json')
    @timer(f"../../generated/timers/{domain_name}/{'_'.join(map(str, generator_params))}_{max_features}/", lambda n, _: f'rules_{n}.json')
    def with_n_rules(n, past_sketches):
        changes = set()
        candidate_sketches = src.sketch_generation.generation.generate_sketches(bools, nums, n, max_features)
        filtered_candidate_sketches = filter(lambda s2: not (any(s2.contains_sketch(s1) for s1 in past_sketches)),
                                             candidate_sketches)
        working_sketches = []
        sketch_number = 0
        for sketch in tqdm(filtered_candidate_sketches):
            sketch_number += 1
            verified = True
            for e, i in enumerate(instance_files):
                feature_vals = calculate_feature_vals(all_states[e], filtered_features, i.removesuffix(".pddl"))
                feature_instance = FeatureInstance(systems[e].graph, systems[e].init, systems[e].goals, feature_vals)

                verified = verify_sketch(sketch, feature_instance, [law1, law2, impl_law])

                if not verified:
                    changes.add((e, i))
                    break
            if verified:
                working_sketches.append(sketch)
        return working_sketches, sketch_number, list(changes)

    past_sketches = []
    for n_rules in range(1, max_rules + 1):
        working_sketches, tested_sketches, stable = with_n_rules(n_rules, past_sketches)
        past_sketches.extend(working_sketches)

    print("RESOURCE USAGE", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__ == '__main__':
    domain_name = "blocks_4_clear"
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

    @timer(f"../../generated/timers/{domain_name}/", lambda: filename)
    def write_all():
        file_dir = f"../../generated/{domain_name}/"
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        run_on_multiple_instances(domain_file, instance_files[:10] + instance_files[20:30], generator_params, max_features, max_rules)
    write_all()
