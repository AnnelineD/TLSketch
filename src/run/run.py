import json
import os

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


def run_on_multiple_instances(domain_file: str, instance_files: list[str]):
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
    params = [5, 5, 5, 5, 5, 3600, 10000]
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

    candidate_sketches = src.sketch_generation.generation.generate_sketches(bools, nums, 1, 1)
    for the_one_sketch in tqdm(candidate_sketches):
        checked = True
        for e, i in enumerate(instance_files):
            feature_vals = calculate_feature_vals(all_states[e], filtered_features, i.removesuffix(".pddl"))
            feature_instance = FeatureInstance(systems[e].graph, systems[e].init, systems[e].goals, feature_vals)

            checked = verify_sketch(the_one_sketch, feature_instance, [law1, law2, exists_impl_law, impl_law])
            if not checked:
                break
        if checked:
            print(the_one_sketch.rules)
            print()
            yield the_one_sketch


if __name__ == '__main__':
    domain_name = "blocks_4_clear"
    directory = f"../../domains/{domain_name}/"
    domain_file = directory + "domain.pddl"

    files = os.listdir(directory)
    files.sort()
    instance_files = list(filter(lambda x: x.startswith('p-'), files))
    # instance_files.remove("domain.pddl")
    # instance_files.remove("domain-with-fix.pddl")
    # instance_files.remove("README")

    filename = "10_instances_5_5_10_10_10_180_100000_1_1_1.json"

    @timer(f"../../generated/timers/{domain_name}/", lambda: filename)
    def write_all():
        file_dir = f"../../generated/{domain_name}/"
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)
        with open(f"../../generated/{domain_name}/" + filename, "w") as f:
            json.dump([s.serialize() for s in run_on_multiple_instances(domain_file, instance_files[0:10])], f)

    write_all()
