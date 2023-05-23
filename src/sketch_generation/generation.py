import dlplan

import examples
import src.transition_system as ts
from src.logics.rules import Feature, SketchRule, Sketch
from src.logics.conditions_effects import *
# from src.logics.rules import RuleListRepr
import itertools
from typing import Generator, TypeVar, Callable
from collections.abc import Iterator



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

"""
def generate_features(vocab: dlplan.VocabularyInfo, states: list[dlplan.State]) -> (list[dlplan.Boolean], list[dlplan.Numerical]):
    generator = construct_feature_generator()
    factory = dlplan.SyntacticElementFactory(vocab)
    string_features: list[str] = generator.generate(factory, 5, 5, 10, 10, 10, 180, 100000, 1, states)      # TODO check these parameters
    boolean_features = [factory.parse_boolean(f) for f in string_features if f.startswith("b_")]
    numerical_features = [factory.parse_numerical(f) for f in string_features if f.startswith("n_")]

    return boolean_features, numerical_features
"""


def get_feature_sets(boolean_features: list[str], numerical_features: list[str], size=3) -> Iterator[(tuple[Boolean, ...], tuple[Numerical, ...])]:
    for i in range(0, size + 1):
        j = size - i
        yield from itertools.product(
            itertools.combinations(boolean_features, i),
            itertools.combinations(numerical_features, j))


def possible_conditions(boolean_features: list[Boolean], numerical_features: list[Numerical]) -> Generator[list[Condition], None, None]:
    n_features: int = len(boolean_features) + len(numerical_features)
    possible_conditions = itertools.product([0, 1, 2], repeat=n_features)      # ((0, 0, 0, 0), (0, 0, 0, 1), (1, 2, 0, 0), ....)

    def convert_num_condition(i: int, f: str) -> NumericalCondition:
        match i:
            case 0: return CNAny(f)
            case 1: return CZero(f)
            case 2: return CGreater(f)

    def convert_bool_condition(i: int, f: str) -> BooleanCondition:
        match i:
            case 0: return CBAny(f)
            case 1: return CNegative(f)
            case 2: return CPositive(f)

    for cs in possible_conditions:
        yield list(map(lambda i, f: convert_num_condition(i, f), cs[:len(numerical_features)], numerical_features)) \
                + list(map(lambda i, f: convert_bool_condition(i, f), cs[len(numerical_features):], boolean_features))


def possible_effects(condition: list[Condition]) -> Iterator[list[Effect]]:
    def match_c(c):
        match c:
            case CZero(x): return [EIncr(x), ENEqual(x), ENAny(x)]
            case CGreater(x): return [EIncr(x), EDecr(x), ENEqual(x), ENAny(x)]
            case CNAny(x): return [EIncr(x), EDecr(x), ENEqual(x), ENAny(x)]
            case CNegative(x): return [EPositive(x), EBEqual(x), EBAny(x)]
            case CPositive(x): return [ENegative(x), EBEqual(x), EBAny(x)]
            case CBAny(x): return [EPositive(x), ENegative(x), EBEqual(x), EBAny(x)]

    print(len(condition))
    for es in itertools.product(*map(match_c, condition)):
        if not all(isinstance(ef, ENAny) or isinstance(ef, EBAny) for ef in es):
            yield es
            #print("returned")


A = TypeVar('A')
B = TypeVar('B')

def dependent_product(it1: Iterator[A], f_it2: Callable[[A], Iterator[B]]) -> Iterator[tuple[A, B]]:
    for a in it1:
        for b in f_it2(a):
            yield (a, b)


C = TypeVar('C')


def all_combinations(it: Iterator[C], n: int) -> Iterator[tuple[C, ...]]:
    """

    :param it:
    :param n:
    :return: tuples of length <= n
    """
    yield from itertools.combinations(it, n)
    #for i, itn in enumerate(itertools.tee(it, n)):
    #    yield from itertools.combinations(itn, i+1)


def generate_rules(boolean_features: list[str], numerical_features: list[str]) -> Iterator[SketchRule]:
    cs: Iterator[list[Condition]] = possible_conditions(boolean_features, numerical_features)
    rs: Iterator[tuple[list[Condition], list[Effect]]] = dependent_product(cs, possible_effects)
    return map(SketchRule.from_tuple, rs)


def generate_sketches(boolean_features: list[str], numerical_features: list[str], max_rules=3, max_features=3) -> Iterator[Sketch]:
    fsets = get_feature_sets(boolean_features, numerical_features, max_features)  # TODO also sets of size < max_features
    for bfs, nfs in fsets:
        rs = generate_rules(bfs, nfs)
        rs_combs = all_combinations(rs, max_rules)
        yield from map(Sketch.from_tuple, rs_combs)
    # return map(Sketch.from_tuple, rs_combs)




"""
def to_policy(sketch: tuple[list[Condition], list[Effect]]) -> dlplan.Policy:
    cs, es = sketch
    builder = dlplan.PolicyBuilder()
    for c in cs:
        match c:
            case BooleanCondition(x): 
                b = builder.add_boolean_feature(c.feature)
                match c:
                    case CPositive(y): builder.add_pos_condition(b)
                    case CNegative(y): builder.add_neg_condition(b)
                    case CBAny(y): pass
            case NumericalCondition(x): 
                n = builder.add_numerical_feature(c.feature)
                match n:
                    case CZero(y): builder.add_eq_condition(n)
                    case CGreater(y): builder.add_gt_condition(n)
                    case CNAny(y): pass
                
    for e in es:
        match e:
    b = builder.add_boolean_feature(boolean)
    n = builder.add_numerical_feature(numerical)

    b_neg_condition_0 = builder.add_neg_condition(b)
    b_bot_effect_0 = builder.add_bot_effect(b)
    n_gt_condition_0 = builder.add_gt_condition(n)
    n_dec_effect_0 = builder.add_dec_effect(n)
    r = builder.add_rule(
        [b_neg_condition_0, n_gt_condition_0],
        [b_bot_effect_0, n_dec_effect_0]
    )
    policy = builder.get_result()
"""
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

