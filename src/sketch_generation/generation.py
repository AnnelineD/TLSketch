# this file contains methods to
#   1. Construct a feature generator with the same parameters as used in Dominik Drexler, Jendrik Seipp,
#   and Hector Geffner. Learning sketches for decomposing planning problems into subproblems of bounded width:
#   Extended version. arXiv preprint arXiv:2203.14852, 2022.
#   2. Generate all possible candidate sketches given a set of features

import itertools
import dlplan

from src.logics.rules import SketchRule, Sketch
from src.logics.conditions_effects import *
from typing import Generator, TypeVar, Callable
from collections.abc import Iterator


def construct_feature_generator() -> dlplan.generator.FeatureGenerator:
    """
    Method from Dominik Drexler, Jendrik Seipp, and Hector Geffner. Proofs, code, and data for the icaps 2022 paper,
    March 2022.

    :return: feature generator with the same parameters as used in Dominik Drexler, Jendrik Seipp,
             and Hector Geffner. Learning sketches for decomposing planning problems into subproblems of bounded width:
             Extended version. arXiv preprint arXiv:2203.14852, 2022.
    """
    feature_generator = dlplan.generator.FeatureGenerator()
    feature_generator.set_generate_concept_distance_numerical(False)
    feature_generator.set_generate_inclusion_boolean(False)
    feature_generator.set_generate_diff_concept(False)
    feature_generator.set_generate_or_concept(False)
    feature_generator.set_generate_subset_concept(False)
    # feature_generator.set_generate_role_distance_numerical(False)     # these methods do not exist in the current version of DLPlan
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


def get_feature_sets(boolean_features: list[str], numerical_features: list[str], size=3) \
                     -> Iterator[(tuple[Boolean, ...], tuple[Numerical, ...])]:
    """
    Generate all possible feature sets that contain a specific number of features
    If there are fewer features than the feature size TODO
    :param boolean_features: The boolean features one can choose from in string form
    :param numerical_features:  The numerical features one can choose from in string form
    :param size: The number of features each set can contain
    :return: A lazy iterator containing all possible feature sets of size 'size', in which boolean and numerical
            features are separated
    """
    for i in range(0, size + 1):
        j = size - i
        yield from itertools.product(
            itertools.combinations(boolean_features, i),
            itertools.combinations(numerical_features, j))


def possible_conditions(boolean_features: list[Boolean], numerical_features: list[Numerical]) -> Generator[
                        list[Condition], None, None]:
    """
    Lazily create all possible conditions that use the provided features
    e.g. possible_conditions('b', 'n') = [[b, n=0], [b, n>0], [b, n?],
                                          [!b, n=0], [!b, n>0], [!b, n?],
                                          [b?, n=0], [b?, n>0], [b?, n?]]
    in which b? or n? is equal to not mentioning them
    :param boolean_features: boolean features represented as strings
    :param numerical_features: numerical features represented as strings
    :return: generator of conditions using the provided features
    """
    n_features: int = len(boolean_features) + len(numerical_features)
    # Each feature can occur in three possible feature conditions. We represent each feature condition by a number
    # and will substitute them afterward. This is because boolean and numerical features use different conditions
    # and this allows us to easily construct a series of all combinations without having to worry about that
    # e.g. for two features possible_combinations will look like:
    # ((0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2))
    possible_combinations = itertools.product([0, 1, 2], repeat=n_features)

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

    for cs in possible_combinations:
        yield list(map(lambda i, f: convert_num_condition(i, f), cs[:len(numerical_features)], numerical_features)) \
            + list(map(lambda i, f: convert_bool_condition(i, f), cs[len(numerical_features):], boolean_features))


def possible_effects(condition: list[Condition]) -> Iterator[list[Effect]]:
    """
    Given a condition, generate all effects that can form a rule together with this condition
    We exclude all effects that don't make sense given the conditions
    (e.g. decreasing a feature when it should be zero in the conditions)
    Important is that all usable features should be present in the conditions, features that can have any value in the
    conditions should be mentioned as CNAny(f) or CBAny(f)
    :param condition: a list of feature conditions
    :return: all effects (consisting of feature effects) that can be reached after the condition, and that use the same
    features as mentioned in the condition
    """
    def match_c(c):
        match c:
            case CZero(x): return [EIncr(x), ENEqual(x), ENAny(x)]
            case CGreater(x): return [EIncr(x), EDecr(x), ENEqual(x), ENAny(x)]
            case CNAny(x): return [EIncr(x), EDecr(x), ENEqual(x), ENAny(x)]
            case CNegative(x): return [EPositive(x), EBEqual(x), EBAny(x)]
            case CPositive(x): return [ENegative(x), EBEqual(x), EBAny(x)]
            case CBAny(x): return [EPositive(x), ENegative(x), EBEqual(x), EBAny(x)]

    for es in itertools.product(*map(match_c, condition)):
        # here we exclude an empty effect (one in which anything is possible) to reduce combinatorial blowup
        if not all(isinstance(ef, ENAny) or isinstance(ef, EBAny) for ef in es):
            yield es


# these help typing the dependent product method
A = TypeVar('A')
B = TypeVar('B')


def dependent_product(it1: Iterator[A], f_it2: Callable[[A], Iterator[B]]) -> Iterator[tuple[A, B]]:
    """
    e.g. dependent_product([1, 2, 3], lambda x -> [x*2, x*4]) = [(1,2), (1, 4), (2, 4), (2, 8), (3, 6), (3, 12)]
    :param it1: An iterator with elements of type A
    :param f_it2: Method that takes an objects of type A and returns an iterator with elements of type B
    :return: An iterator with tuples in which the first element e1 was in it1, and the second element is in f_it2(e1)
    """
    for a in it1:
        for b in f_it2(a):
            yield (a, b)


C = TypeVar('C')


def all_combinations(it: Iterator[C], n: int) -> Iterator[tuple[C, ...]]:
    """
    Take all subsequences of n elements of an iterator
    :param it: The iterator to take elements from
    :param n: Number of elements per subsequence
    :return: tuples of length == n with elements from it
    """
    yield from itertools.combinations(it, n)
    # for i, itn in enumerate(itertools.tee(it, n)):
    #    yield from itertools.combinations(itn, i+1)


def generate_rules(boolean_features: list[str], numerical_features: list[str]) -> Iterator[SketchRule]:
    """
    Lazily generate all sketch rules that can be made with the provided features
    :param boolean_features: a list of boolean features represented as strings
    :param numerical_features: a list of numerical features represented as strings
    :return: An iterator of sketch rules using the provided features
    """
    cs: Iterator[list[Condition]] = possible_conditions(boolean_features, numerical_features)
    rs: Iterator[tuple[list[Condition], list[Effect]]] = dependent_product(cs, possible_effects)
    return map(SketchRule.from_tuple, rs)


def generate_sketches(boolean_features: list[str], numerical_features: list[str], num_rules=3, max_features=3) -> \
        Iterator[Sketch]:
    """
    Lazily construct all candidate sketches with n rules and maximum m features that use the provided features
    :param boolean_features: a list of boolean features represented as strings that can be used in the sketches
    :param numerical_features: a list of numerical features represented as strings that can be used in the sketches
    :param num_rules: the number of rules the sketches should contain
    :param max_features: the maximum number of features a sketch can have
    :return: An iterator of sketches
    """
    # First create all possible sets of 'max_features' features
    # We don't need to create sets with less than 'max_features' because rules with fewer features will be constructed
    # automatically due to the "Any" conditions and effects
    fsets = {s for s in get_feature_sets(boolean_features, numerical_features, max_features)}

    for bfs, nfs in fsets:      # For each set generate all possible sketches that use the features from this set
        rs = generate_rules(bfs, nfs)
        rs_combs = all_combinations(rs, num_rules)
        yield from map(Sketch.from_tuple, rs_combs)
