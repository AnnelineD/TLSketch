# Classes that represent sketch rules and sketches
# There are two types of Sketches that consist of their corresponding sketch rules
# Expanded rules have conditions and effects in as lists of feature variables (e.g. n=5)
# Sketch rules have conditions and effects as lists of feature conditions and feature effects (e.g. n↓)
# Sketch rules can be expanded into expanded sketch rules when the minimum and maximum values of the used features are
# known


import itertools
from dataclasses import dataclass
from typing import Self

from ..logics.conditions_effects import Feature, Condition, CGreater, CZero, CPositive, CNegative, CNAny, CBAny, \
    Effect, EPositive, ENegative, EBEqual, EBAny, NumericalEffect, EDecr, EIncr, ENEqual, ENAny
from ..logics.feature_vars import FeatureVar, NumericalVar, BooleanVar

import dlplan.policy as dlpolicy


class Rule:
    """
    A rule consists of conditions and effects
    """
    conditions: 'C'
    effects: 'E'


"""
class LTLRule(Rule):
    conditions: LTLFormula  # with vars of type FeatureVar
    effects: LTLFormula     # with vars of type FeatureVar

    def __init__(self, c: LTLFormula, e: LTLFormula):
        for v in c.get_vars():
            assert isinstance(v, FeatureVar)
        for v in e.get_vars():
            assert isinstance(v, FeatureVar)

        self.conditions = c
        self.effects = e

    def __str__(self) -> str:
        return f"conditions: {self.conditions.show()}    effects: {self.effects.show()}"

    def get_features(self):
        return {v.data for v in self.conditions.get_vars()}.union({e.data for e in self.effects.get_vars()})


class LTLSketch:
    rules: list[LTLRule]

    def __init__(self, rules: list[LTLRule]):
        self.rules = rules

    def n_rules(self):
        return len(self.rules)

    def get_features(self):
        return {f for r in self.rules for f in r.get_features()}
"""


class ExpandedRule(Rule):
    """
    Instance dependent representation of a sketch rule in which feature conditions and feature effects are represented
    as Feature Variables.
    """
    conditions: list[FeatureVar]
    effects: list[FeatureVar]

    def __init__(self, c: list[FeatureVar], e: list[FeatureVar]):
        """ this code can be added for safety but significantly slows down the execution time of the program
        for v in c:
            assert isinstance(v, FeatureVar)
        for v in e:
            assert isinstance(v, FeatureVar)
        """
        self.conditions = c
        self.effects = e

    def show(self) -> str:
        """
        Convert rule to an easily readable and printable string
        :return: Compact human-readable representation
        """
        return f"conditions: {', '.join(map(lambda x: x.show(), self.conditions))}    " \
               f"effects: {', '.join(map(lambda x: x.show(), self.conditions))}"

    def get_features(self) -> set[Feature]:
        """
        :return: all features that are used in this sketch rule
        """
        return {v.data for v in self.conditions}.union({e.data for e in self.effects})


class ExpandedSketch:
    """
    Instance dependent sketch representation that is consists of expanded sketch rules
    """
    rules: list[ExpandedRule]

    def __init__(self, rules: list[ExpandedRule]):
        self.rules = rules

    def n_rules(self):
        return len(self.rules)

    def get_features(self):
        """
        :return: all features used in the sketch
        """
        return {f for r in self.rules for f in r.get_features()}


@dataclass
class SketchRule(Rule):
    """
    Representation of a sketch rule
    """
    conditions: list[Condition]
    effects: list[Effect]

    # TODO simplify in constructor

    @classmethod
    def from_dlplan_rule(cls, rule: dlpolicy.Rule) -> Self:
        """
        Convert a sketch rule from the DLPlan library into an object of the SketchRule class
        :param rule: sketch rule represented as a Rule object from the DLPlan library
        :return: Object of this SketchRule class
        """
        return cls([Condition.from_dlplan(c) for c in rule.get_conditions()],
                   [Effect.from_dlplan(e) for e in rule.get_effects()])

    @classmethod
    def from_tuple(cls, tup: tuple[list[Condition], list[Effect]]) -> Self:
        """
        Construct a sketch rule from a tuple containing the conditions and effects
        :param tup: tuple of conditions and effects
        :return: sketch rule
        """
        return cls(tup[0], tup[1])

    @classmethod
    def deserialize(cls, sr: tuple[list[str], list[str]]) -> Self:
        """
        Construct a sketch rule from a json readable object; a tuple containing feature conditions and feature effects
        in the form of strings
        This method is necessary for cashing
        :param sr: tuple containing a list of feature conditions in string representation and a list of feature effects
                   in string representation
        :return: sketch rule
        """
        return cls(list(map(eval, sr[0])), list(map(eval, sr[1])))

    def serialize(self) -> tuple[list[str], list[str]]:
        """
        Convert a sketch rule into a json readable objects
        Necessary for cashing
        :return: tuple containing a list of feature conditions in string representation and a list of feature effects
                   in string representation
        """
        return list(map(str, self.conditions)), list(map(str, self.effects))

    def get_condition_features(self) -> set[Feature]:
        """:return: all features that appear in the feature conditions of the sketch rule"""
        return {c.feature for c in self.conditions if not isinstance(c, CNAny) or isinstance(c, CBAny)}

    def get_effect_features(self) -> set[Feature]:
        """:return: all features that appear in the feature effects of the sketch rule"""
        return {e.feature for e in self.effects}

    def get_features(self) -> set[Feature]:
        """:return: all features that appear in the sketch rule"""
        return self.get_condition_features().union(self.get_effect_features())

    def simplify(self):
        """Remove all Any conditions and Any effects from the sketch rule since saying that a feature can have any value
        is equivalent to not mentioning that feature at all"""
        return SketchRule([c for c in self.conditions if not (isinstance(c, CNAny) or isinstance(c, CBAny))],
                          [e for e in self.effects if not (isinstance(e, ENAny) or isinstance(e, EBAny))])

    """
    def to_ltl(self, bounds: dict[str, (int, int)]) -> list['LTLRule']:
        # TODO throw error when a numerical feature is missing from the bound dict or if there is a var of wrong type
        # TODO what to do with rules without effects -> can't exist
        assert(len(self.effects) > 0)
        assert(all([l <= u for (l, u) in bounds.values()]))
        features: set[Feature] = set()  # Get only the features that are present in conditions or effects
        # We do not need features that are not mentioned in conditions and are unchanged in the effects
        for ef in self.effects:
            match ef:
                case EBEqual(f): features.add(f)
                case NumericalEffect(f): features.add(f)

        options = {f: None for f in features}
        condition_vars: set[Condition] = set(self.conditions)

        for v in condition_vars:
            if v.feature in features:
                match v:
                    case CGreater(f): options[v.feature] = [NumericalVar(f, i) for i in range(max(bounds[f][0], 1), bounds[f][1] + 1)]
                    case CZero(f): options[v.feature] = [NumericalVar(f, 0)]
                    case CPositive(f): options[v.feature] = [BooleanVar(f, True)]
                    case CNegative(f): options[v.feature] = [BooleanVar(f, False)]
                    case CNAny(f): pass
                    case CBAny(f): pass

        # If a feature is not mentioned in the conditions, but it is in the effect we should also know its value
        for f in options:
            if not options[f]:
                match f:
                    case x if x.startswith("n_"): options[f] = [NumericalVar(f, i) for i in range(bounds[f][0], bounds[f][1] + 1)]
                    case x if x.startswith("b_"): options[f] = [BooleanVar(f, True), BooleanVar(f, False)]
                    case _: print("something went wrong while filling in the feature values")        # TODO raise error

        condition_combinations: list[dict[Feature, FeatureVar]] = [dict(zip(options.keys(), values)) for values in itertools.product(*options.values())]

        effect_vars: set[Effect] = set(e for e in self.effects if not (isinstance(e, EBAny) or isinstance(e, ENAny)))
        # print("effects", effect_vars)
        new_rules = []

        for c_dict in condition_combinations:
            # new_effect = rule.effects
            if not self.effects:
                new_effect = Bottom
            else:
                new_effect = reduce(And, map(Var, effect_vars))
            if len(c_dict) == 0:
                new_condition = Top()
            elif len(c_dict) == 1:
                new_condition = list(c_dict.values())[0]
            else:
                new_condition = reduce(And, c_dict.values())

            for e in effect_vars:
                match e:
                    case EPositive(f): new_effect = new_effect.replace(Var(e), BooleanVar(f, True))
                    case ENegative(f): new_effect = new_effect.replace(Var(e), BooleanVar(f, False))
                    case EBEqual(f): new_effect = new_effect.replace(Var(e), BooleanVar(f, c_dict[f].value))
                    case EDecr(f):
                        if c_dict[f].value == bounds[f][0]:
                            new_effect = Bottom()  # The effect is impossible to reach because the feature cannot decrease anymore
                        # elif c_dict[f].value == bounds[f][0] + 1:
                            # new_effect = new_effect.replace(Var(e), NumericalVar(f, 0))
                        else:
                            new_effect = new_effect.replace(Var(e), reduce(Or, map(lambda v: NumericalVar(f, v), range(bounds[f][0], c_dict[f].value))))
                    case EIncr(f):
                        if bounds[f][1] - c_dict[f].value == 0:
                            new_effect = Bottom()  # The effect is impossible to reach because the feature cannot increase anymore
                        elif bounds[f][1] - c_dict[f].value <= 1:
                            new_effect = new_effect.replace(Var(e), NumericalVar(f, bounds[f][1]))
                        else:
                            new_effect = new_effect.replace(Var(e), reduce(Or, map(lambda v: NumericalVar(f, v), range(c_dict[f].value + 1, bounds[f][1] + 1))))
                    case ENEqual(f): new_effect = new_effect.replace(Var(e), NumericalVar(f, c_dict[f].value))
                    case EBAny(f): raise NotImplementedError
                    case ENAny(f): raise NotImplementedError
            # if LTLRule(new_condition, new_effect) not in
            if not new_effect == Bottom():
                # print("c:", new_condition, "e: ", new_effect)
                new_rules.append(LTLRule(new_condition, new_effect))
        # print("new_rules", *new_rules)
        return new_rules
    """

    def expand(self, bounds: dict[str, (int, int)]) -> list[ExpandedRule]:
        """
        Expand a sketch rule into an expanded sketch rule using the bounds on the numerical features
        :param bounds: for each numerical feature (in string representation) a lower and upper bound
        :return: A list of expanded sketch rules
        """
        # TODO throw error when a numerical feature is missing from the bound dict or if there is a var of wrong type
        assert (len(self.effects) > 0)      # TODO allow empty effects
        assert (all([l <= u for (l, u) in bounds.values()]))    # lower bounds should be lower than upper bounds
        features: set[Feature] = set()  # Get only the features that are present in conditions or effects
        # We do not need to expand conditions and effects of features that are not mentioned in conditions and are
        # unchanged in the effects
        for ef in self.effects:
            match ef:
                case EBEqual(f):
                    features.add(f)
                case NumericalEffect(f):
                    features.add(f)

        options = {f: None for f in features}
        condition_vars: set[Condition] = set(self.conditions)

        for v in condition_vars:
            if v.feature in features:
                match v:
                    case CGreater(f):
                        options[v.feature] = [NumericalVar(f, i, "=") for i in
                                              range(max(bounds[f][0], 1), bounds[f][1] + 1)]
                    case CZero(f):
                        options[v.feature] = [NumericalVar(f, 0, "=")]
                    case CPositive(f):
                        options[v.feature] = [BooleanVar(f, True, "=")]
                    case CNegative(f):
                        options[v.feature] = [BooleanVar(f, False, "=")]
                    case CNAny(f):
                        pass
                    case CBAny(f):
                        pass

        # If a feature is not mentioned in the conditions, but it is in the effect we should also know its value
        for f in options:
            if not options[f]:
                match f:
                    case x if x.startswith("n_"):
                        options[f] = [NumericalVar(f, i, "=") for i in range(bounds[f][0], bounds[f][1] + 1)]
                    case x if x.startswith("b_"):
                        options[f] = [BooleanVar(f, True, "="), BooleanVar(f, False, "=")]
                    case _:
                        print("something went wrong while filling in the feature values")  # TODO raise error

        condition_combinations: list[dict[Feature, FeatureVar]] = [dict(zip(options.keys(), values)) for values in
                                                                   itertools.product(*options.values())]

        new_rules = list[ExpandedRule]()

        def to_feature_var(c: Condition) -> FeatureVar:
            match c:
                case CGreater(f):
                    return NumericalVar(f, 0, ">")
                case CZero(f):
                    return NumericalVar(f, 0, "=")
                case CPositive(f):
                    return BooleanVar(f, True, "=")
                case CNegative(f):
                    return BooleanVar(f, False, "=")
                case CNAny(f):
                    pass
                case CBAny(f):
                    pass

        for c_dict in condition_combinations:
            new_effect = []
            new_condition = list([to_feature_var(c) for c in self.conditions if
                                  c.feature not in features and to_feature_var(c) is not None]) + list(c_dict.values())

            for e in self.effects:
                match e:
                    case EPositive(f):
                        new_effect.append(BooleanVar(f, True, "="))
                    case ENegative(f):
                        new_effect.append(BooleanVar(f, False, "="))
                    case EBEqual(f):
                        new_effect.append(BooleanVar(f, c_dict[f].value, "="))
                    case EDecr(f):
                        new_effect.append(NumericalVar(f, c_dict[f].value, "<"))
                    case EIncr(f):
                        new_effect.append(NumericalVar(f, c_dict[f].value, ">"))
                    case ENEqual(f):
                        new_effect.append(NumericalVar(f, c_dict[f].value, "="))
                    case EBAny(f):
                        pass
                    case ENAny(f):
                        pass
            new_rules.append(ExpandedRule(new_condition, new_effect))
        return new_rules


@dataclass
class Sketch:
    """
    Sketch consisting of sketch rules
    """
    rules: list[SketchRule]

    def __init__(self, rules: list[SketchRule]):
        self.rules = rules

    @classmethod
    def from_policy(cls, policy: dlpolicy.Policy):
        return Sketch([SketchRule.from_dlplan_rule(r) for r in policy.get_rules()])

    @classmethod
    def from_tuple(cls, tup: tuple[SketchRule]):
        return cls(list(tup))

    """
    def to_ltl(self, bounds: dict[str, (int, int)]) -> LTLSketch:
        return LTLSketch([nr for r in self.rules for nr in r.to_ltl(bounds)])
    """

    def expand(self, bounds: dict[str, (int, int)]) -> ExpandedSketch:
        """
        Expand a sketch into an expanded sketch using the bounds on the numerical features
        :param bounds: for each numerical feature (in string representation) a lower and upper bound
        :return: An expanded sketch
        """
        return ExpandedSketch([nr for r in self.rules for nr in r.expand(bounds)])

    def serialize(self) -> list[tuple[list[str], list[str]]]:
        """
        Convert a sketch into a json readable object
        This method is necessary for cashing
        """
        return [r.serialize() for r in self.rules]

    @classmethod
    def deserialize(cls, rs: list[tuple[list[str], list[str]]]) -> Self:
        """
        Construct a sketch from a json readable object
        This method is necessary for cashing
        """
        return Sketch([SketchRule.deserialize(r) for r in rs])

    def contains_sketch(self, other: Self) -> bool:
        """
        Check whether this sketch contains all rules from another sketch, i.e. check whether self.rules ⊆ other.rules
        :param other: Sketch
        :return: true if this sketch contains all rules from the other sketch, false otherwise
        """
        return all(r in self.rules for r in other.rules)

    def get_features(self) -> set[Feature]:
        """:return: all features used in this sketch"""
        return {f for r in self.rules for f in r.get_features()}

    def simplify(self) -> Self:
        """
        Remove all Any conditions and Any effects from the sketch rule since saying that a feature can have any value
        is equivalent to not mentioning that feature at all
        :return: New Sketch object in which all Any conditions and Any effects are removed
        """
        return Sketch([r.simplify() for r in self.rules])
