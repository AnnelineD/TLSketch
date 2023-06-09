import itertools
#from collections import namedtuple
from dataclasses import dataclass
from functools import reduce

from ltl import *

from ..logics.conditions_effects import *
from ..logics.feature_vars import *


#Rule = namedtuple("Rule", "conditions effects")

class Rule:
    conditions: 'C'
    effects: 'E'



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


class ExpandedRule(Rule):
    conditions: list[FeatureVar]  # with vars of type FeatureVar
    effects: list[FeatureVar]     # with vars of type FeatureVar

    def __init__(self, c: list[FeatureVar], e: list[FeatureVar]):
        """
        for v in c:
            assert isinstance(v, FeatureVar)
        for v in e:
            assert isinstance(v, FeatureVar)
        """
        self.conditions = c
        self.effects = e

    def __str__(self) -> str:
        return f"conditions: {', '.join(map(lambda x: x.show(), self.conditions))}    " \
               f"effects: {', '.join(map(lambda x: x.show(), self.conditions))}"

    def get_features(self):
        return {v.data for v in self.conditions}.union({e.data for e in self.effects})


class ExpandedSketch:
    rules: list[ExpandedRule]

    def __init__(self, rules: list[ExpandedRule]):
        self.rules = rules

    def n_rules(self):
        return len(self.rules)

    def get_features(self):
        return {f for r in self.rules for f in r.get_features()}


@dataclass
class SketchRule(Rule):
    conditions: list[Condition]
    effects: list[Effect]

    @classmethod
    def from_dlplan_rule(cls, rule: dlplan.Rule):
        return SketchRule([cond_from_dlplan(c) for c in rule.get_conditions()],
                          [eff_from_dlplan(e) for e in rule.get_effects()])

    @classmethod
    def from_tuple(cls, tup: tuple[list[Condition], list[Effect]]):
        return cls(tup[0], tup[1])

    @classmethod
    def deserialize(cls, sr: tuple[list[str], list[str]]):
        return cls(list(map(eval, sr[0])), list(map(eval, sr[1])))

    def serialize(self) -> tuple[list[str], list[str]]:
        return list(map(str, self.conditions)), list(map(str, self.effects))

    def get_condition_features(self) -> set[Feature]:
        return {c.feature for c in self.conditions if not isinstance(c, CNAny) or isinstance(c, CBAny)}

    def get_effect_features(self) -> set[Feature]:
        return {e.feature for e in self.effects}

    def get_features(self) -> set[Feature]:
        return self.get_condition_features().union(self.get_effect_features())

    def to_ltl(self, bounds: dict[str, (int, int)]) -> list['LTLRule']:
        # TODO throw error when a numerical feature is missing from the bound dict or if there is a var of wrong type
        # TODO what to do with rules without effects -> can't exist
        assert(len(self.effects) > 0)
        assert(all([l <= u for (l, u) in bounds.values()]))
        features: set[Feature] = self.get_condition_features()   # Get only the features that are present in conditions or effects
        # We do not need features that are not mentioned in conditions and are unchanged in the effects
        for ef in self.effects:
            match ef:
                case EBEqual(f): features.add(f)
                case NumericalEffect(f): features.add(f)

        options = {f: None for f in features}
        condition_vars: set[Condition] = set(self.conditions)

        for v in condition_vars:
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

    def expand(self, bounds: dict[str, (int, int)]) -> list[ExpandedRule]:
        # TODO throw error when a numerical feature is missing from the bound dict or if there is a var of wrong type
        # TODO what to do with rules without effects -> can't exist
        assert(len(self.effects) > 0)
        assert(all([l <= u for (l, u) in bounds.values()]))
        features: set[Feature] = self.get_condition_features()   # Get only the features that are present in conditions or effects
        # We do not need features that are not mentioned in conditions and are unchanged in the effects
        for ef in self.effects:
            match ef:
                case EBEqual(f): features.add(f)
                case NumericalEffect(f): features.add(f)

        options = {f: None for f in features}
        condition_vars: set[Condition] = set(self.conditions)

        for v in condition_vars:
            match v:
                case CGreater(f): options[v.feature] = [NumericalVar(f, i, "=") for i in range(max(bounds[f][0], 1), bounds[f][1] + 1)]
                case CZero(f): options[v.feature] = [NumericalVar(f, 0, "=")]
                case CPositive(f): options[v.feature] = [BooleanVar(f, True, "=")]
                case CNegative(f): options[v.feature] = [BooleanVar(f, False, "=")]
                case CNAny(f): pass
                case CBAny(f): pass

        # If a feature is not mentioned in the conditions, but it is in the effect we should also know its value
        for f in options:
            if not options[f]:
                match f:
                    case x if x.startswith("n_"): options[f] = [NumericalVar(f, i, "=") for i in range(bounds[f][0], bounds[f][1] + 1)]
                    case x if x.startswith("b_"): options[f] = [BooleanVar(f, True, "="), BooleanVar(f, False, "=")]
                    case _: print("something went wrong while filling in the feature values")        # TODO raise error

        condition_combinations: list[dict[Feature, FeatureVar]] = [dict(zip(options.keys(), values)) for values in itertools.product(*options.values())]

        # effect_vars: set[Effect] = set(e for e in self.effects if not (isinstance(e, EBAny) or isinstance(e, ENAny)))
        # print("effects", effect_vars)
        new_rules = list[ExpandedRule]()

        for c_dict in condition_combinations:
            new_effect = []
            new_condition = list(c_dict.values())

            for e in self.effects:
                match e:
                    case EPositive(f): new_effect.append(BooleanVar(f, True, "="))
                    case ENegative(f): new_effect.append(BooleanVar(f, False, "="))
                    case EBEqual(f): new_effect.append(BooleanVar(f, c_dict[f].value, "="))
                    case EDecr(f): new_effect.append(NumericalVar(f, c_dict[f].value, "<"))
                    case EIncr(f): new_effect.append(NumericalVar(f, c_dict[f].value, ">"))
                    case ENEqual(f): new_effect.append(NumericalVar(f, c_dict[f].value, "="))
                    case EBAny(f): pass
                    case ENAny(f): pass
            # if LTLRule(new_condition, new_effect) not in
            new_rules.append(ExpandedRule(new_condition, new_effect))
        # print("new_rules", *new_rules)
        return new_rules

@dataclass
class Sketch:
    rules: list[SketchRule]

    def __init__(self, rules: list[SketchRule]):
        self.rules = rules

    @classmethod
    def from_policy(cls, policy: dlplan.Policy):
        return Sketch([SketchRule.from_dlplan_rule(r) for r in policy.get_rules()])

    @classmethod
    def from_tuple(cls, tup: tuple[SketchRule]):
        return cls(list(tup))

    def to_ltl(self, bounds: dict[str, (int, int)]) -> LTLSketch:
        return LTLSketch([nr for r in self.rules for nr in r.to_ltl(bounds)])

    def expand(self, bounds: dict[str, (int, int)]) -> ExpandedSketch:
        return ExpandedSketch([nr for r in self.rules for nr in r.expand(bounds)])

    def serialize(self):
        return [r.serialize() for r in self.rules]

    @classmethod
    def deserialize(cls, rs: list):
        return Sketch([SketchRule.deserialize(r) for r in rs])

    def contains_sketch(self, other):
        return all(r in self.rules for r in other.rules)



