import src.sketch_generation.generation
import src.transition_system as ts
import dlplan

from src.logics.conditions_effects import Feature
from src.sketch_generation.generation import construct_feature_generator
from src.file_manager.cashing import cache_to_file
from src.sketch_verification.feature_instance import FeatureInstance
from src.sketch_verification.verify import verify_sketch
from src.sketch_verification.laws import law1, law2, law3


def run():
    domain = ts.tarski.load_domain("../../miconic/domain.pddl")

    instance = ts.tarski.load_instance("../../miconic/domain.pddl", "../../miconic/p-2-2-2.pddl")
    transition_system = ts.tarski.tarski_to_transition_system(instance)
    dlinstance = ts.conversions.dlinstance_from_tarski(domain, instance)
    dlstates = [ts.dlplan.dlstate_from_state(s, dlinstance) for s in transition_system.states]

    factory = dlplan.SyntacticElementFactory(dlinstance.get_vocabulary_info())
    generator = construct_feature_generator()

    def named_feature_file(factory, x1, x2, x3, x4, x5, x6, x7, x8, dlstates: list[dlplan.State]):
        return f"{instance.domain_name}/features/{x1}_{x2}_{x3}_{x4}_{x5}_{x6}_{x7}_{x8}.json"

    cached_generate = cache_to_file("../../cache/", lambda x: x, lambda x: x, named_feature_file)(generator.generate)
    params = [5, 5, 10, 10, 10, 180, 100000, 1]
    string_features: list[str] = list(filter(lambda x: x.startswith("n_") or x.startswith("b_"), cached_generate(factory, *params, dlstates)))      # TODO check these parameters
    bools = [f for f in string_features if f.startswith("b_")]
    nums = [f for f in string_features if f.startswith("n_")]

    def named_feature_vals(dlstates, string_features, factory) -> str:
        return f"{instance.domain_name}/features/{'_'.join(map(str, params))}/" \
               f"{'_'.join([c.name for c in instance.language.constants()])}_{instance.goal.__repr__().replace(' ', '')}.json"

    @cache_to_file("../../cache/", lambda x: x, lambda x: x, named_feature_vals)
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


if __name__ == '__main__':
    run()

