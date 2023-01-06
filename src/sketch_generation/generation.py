import dlplan

import examples
import src.transition_system as ts
from src.logics.rules import Feature
from src.logics.conditions_effects import *
import itertools
from typing import Generator, TypeVar, Callable

"""
class SketchRule:
    features: list[Feature]
    conditions: list[Condition]
    effects: list[Effect]

    def __init__(self, features, conditions, effects):
        self.features = features
        self.conditions = conditions
        self.effects = effects
"""

# method from Drexler code
def construct_feature_generator():
    feature_generator = dlplan.FeatureGenerator()
    feature_generator.set_generate_concept_distance_numerical(False)
    feature_generator.set_generate_inclusion_boolean(False)
    feature_generator.set_generate_diff_concept(False)
    feature_generator.set_generate_or_concept(False)
    feature_generator.set_generate_subset_concept(False)
    # feature_generator.set_generate_role_distance_numerical(False)
    # feature_generator.set_generate_sum_concept_distance_numerical(False)
    # feature_generator.set_generate_sum_role_distance_numerical(False)
    feature_generator.set_generate_and_role(False)
    feature_generator.set_generate_compose_role(False)
    feature_generator.set_generate_diff_role(False)
    feature_generator.set_generate_identity_role(False)
    feature_generator.set_generate_not_role(False)
    feature_generator.set_generate_or_role(False)
    feature_generator.set_generate_top_role(False)
    feature_generator.set_generate_transitive_reflexive_closure_role(False)
    return feature_generator


def generate_features(vocab: dlplan.VocabularyInfo, states: list[dlplan.State]) -> (list[dlplan.Boolean], list[dlplan.Numerical]):
    generator = construct_feature_generator()
    factory = dlplan.SyntacticElementFactory(vocab)
    string_features: list[str] = generator.generate(factory, 5, 5, 10, 10, 10, 180, 100000, 1, states)      # TODO check these parameters
    boolean_features = [factory.parse_boolean(f) for f in string_features if f.startswith("b_")]
    numerical_features = [factory.parse_numerical(f) for f in string_features if f.startswith("n_")]

    return boolean_features, numerical_features


def get_feature_sets(boolean_features: list[dlplan.Boolean], numerical_features: list[dlplan.Numerical], size = 3) -> list[(list[dlplan.Boolean], list[dlplan.Numerical])]:
    pass


def possible_conditions(boolean_features: list[dlplan.Boolean], numerical_features: list[dlplan.Numerical]) -> Generator[list[Condition], None, None]:
    n_features: int = len(boolean_features) + len(numerical_features)
    possible_conditions = itertools.product([0, 1, 2], repeat=n_features)      # ((0, 0, 0, 0), (0, 0, 0, 1), (1, 2, 0, 0), ....)

    def convert_num_condition(i: int, f: dlplan.Numerical) -> NumericalCondition:
        match i:
            case 0: return CNAny(f)
            case 1: return CZero(f)
            case 2: return CGreater(f)

    def convert_bool_condition(i: int, f: dlplan.Boolean) -> BooleanCondition:
        match i:
            case 0: return CBAny(f)
            case 1: return CNegative(f)
            case 2: return CPositive(f)

    for cs in possible_conditions:
        yield list(map(lambda i, f: convert_num_condition(i, f), cs[:len(numerical_features)], numerical_features)) \
                + list(map(lambda i, f: convert_bool_condition(i, f), cs[len(numerical_features):], boolean_features))


def possible_effects(condition: list[Condition]) -> Generator[list[Effect], None, None]:
    def match_c(c):
        match c:
            case CZero(x): return [ENAny(x), EIncr(x), ENEqual(x)]
            case CGreater(x): return [ENAny(x), EIncr(x), EDecr(x), ENEqual(x)]
            case CNAny(x): return [ENAny(x), EIncr(x), EDecr(x), ENEqual(x)]
            case CNegative(x): return [EBAny(x), EPositive(x), EBEqual(x)]
            case CPositive(x): return [EBAny(x), ENegative(x), EBEqual(x)]
            case CBAny(x): return [EBAny(x), EPositive(x), ENegative(x), EBEqual(x)]

    yield from itertools.product(*[match_c(c) for c in condition])

A = TypeVar('A')
B = TypeVar('B')
from collections.abc import Iterator
def dependent_product(it1: Iterator[A], f_it2: Callable[[A], Iterator[B]]) -> Iterator[tuple[A, B]]:
    for a in it1:
        for b in f_it2(a):
            yield (a, b)

from itertools import islice

def all_combinations(it, n):
    for i, itn in enumerate(itertools.tee(it, n)):
        yield from itertools.combinations(itn, i+1)

def generate_sketches(boolean_features: list[dlplan.Boolean], numerical_features: list[dlplan.Numerical], max_rules=4):
    cs = possible_conditions(boolean_features, numerical_features)
    rs = dependent_product(cs, possible_effects)
    return all_combinations(rs, max_rules)



"""
def generate_possible_rules(boolean_features: list[dlplan.Boolean], numerical_features: list[dlplan.Numerical]) -> list[SketchRule]:
    n_features: int = len(boolean_features) + len(numerical_features)
    possible_conditions = itertools.product([0, 1, 2], repeat=n_features)
    possible_effects = itertools.product([0, 1, 2, 3], repeat=n_features)

    def convert_num_condition(i: int, f: dlplan.Numerical) -> NumericalCondition:
        match i:
            case 0: return CNAny(f)
            case 1: return CZero(f)
            case 2: return CGreater(f)

    def convert_bool_condition(i: int, f: dlplan.Boolean) -> BooleanCondition:
        match i:
            case 0: return CBAny(f)
            case 1: return CNegative(f)
            case 2: return CPositive(f)

    def convert_num_effect(i: int, f: dlplan.Numerical) -> NumericalEffect:
        match i:
            case 0: return ENAny(f)
            case 1: return EDecr(f)
            case 2: return EIncr(f)
            case 3: return ENEqual(f)

    def convert_bool_effect(i: int, f: dlplan.Boolean) -> BooleanEffect:
        match i:
            case 0: return EBAny(f)
            case 1: return ENegative(f)
            case 2: return EPositive(f)
            case 3: return EBEqual(f)

    possible_rules = itertools.product(possible_conditions, possible_effects)

    for cs, es in possible_rules:
        conditions: list[Condition] = \
            list(map(lambda i, f: convert_num_condition(i, f), cs[:len(numerical_features)], numerical_features)) \
            + list(map(lambda i, f: convert_bool_condition(i, f), cs[len(numerical_features):], boolean_features))

        effects: list[Effect] = \
            list(map(lambda i, f: convert_num_effect(i, f), es[:len(numerical_features)], numerical_features)) \
            + list(map(lambda i, f: convert_bool_effect(i, f), es[len(numerical_features):], boolean_features))

        yield SketchRule(boolean_features + numerical_features, conditions, effects)
"""

if __name__ == '__main__':
    domain = examples.Gripper()
    # bools, nums = generate_features(domain.dl_system().instance_info.get_vocabulary_info(), domain.dl_system().states)
    bools = domain.sketch_1().get_boolean_features()
    nums = domain.sketch_1().get_numerical_features()
    print(len(bools) + len(nums))
    for e, r in enumerate(generate_possible_rules(bools, nums)):
        print(e, r.conditions, r.effects)

