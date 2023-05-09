import itertools
from collections import namedtuple
from functools import reduce

from ltl import *

from ..logics.conditions_effects import *
from ..logics.feature_vars import *


Rule = namedtuple("Rule", "conditions effects")


class LTLRule(Rule):
    conditions: LTLFormula  # with vars of type FeatureVar
    effects: LTLFormula     # with vars of type FeatureVar

    def __new__(cls, c: LTLFormula, e: LTLFormula):
        self = super(LTLRule, cls).__new__(cls, c, e)
        for v in c.get_vars():
            assert isinstance(v, FeatureVar)
        for v in e.get_vars():
            assert isinstance(v, FeatureVar)

        return self

    def show(self) -> str:
        return f"conditions: {self.conditions.show()}    effects: {self.effects.show()}"


class LTLSketch:
    rules: list[LTLRule]

    def __init__(self, rules: list[LTLRule]):
        self.rules = rules

    def n_rules(self):
        return len(self.rules)


class SketchRule(Rule):
    conditions: list[Condition]
    effects: list[Effect]

    @classmethod
    def from_dlplan_rule(cls, rule: dlplan.Rule):
        return SketchRule([cond_from_dlplan(c) for c in rule.get_conditions()],
                          [eff_from_dlplan(e) for e in rule.get_effects()])

    def get_condition_features(self) -> set[Feature]:
        return {c.feature for c in self.conditions}

    def get_effect_features(self) -> set[Feature]:
        return {e.feature for e in self.effects}

    def get_features(self) -> set[Feature]:
        return self.get_condition_features().union(self.get_effect_features())

    def to_ltl(self, bounds: dict[str, int]) -> list['LTLRule']:
        # TODO throw error when a numerical feature is missing from the bound dict or if there is a var of wrong type
        # TODO what to do with rules without effects
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
                case CGreater(f): options[v.feature] = [NumericalVar(f, i) for i in range(1, bounds[f.compute_repr()] + 1)]
                case CZero(f): options[v.feature] = [NumericalVar(f, 0)]
                case CPositive(f): options[v.feature] = [BooleanVar(f, True)]
                case CNegative(f): options[v.feature] = [BooleanVar(f, False)]
                case CNAny(f): pass
                case CBAny(f): pass

        # If a feature is not mentioned in the conditions, but it is in the effect we should also know its value
        for f in options:
            if not options[f]:
                match f:
                    case x if isinstance(x, dlplan.Numerical): options[f] = [NumericalVar(f, i) for i in range(0, bounds[f.compute_repr()] + 1)]
                    case x if isinstance(x, dlplan.Boolean): options[f] = [BooleanVar(f, True), BooleanVar(f, False)]
                    case _: print("something went wrong while filling in the feature values")        # TODO raise error

        condition_combinations: list[dict[Feature, FeatureVar]] = [dict(zip(options.keys(), values)) for values in itertools.product(*options.values())]

        effect_vars: set[Effect] = set(self.effects)
        new_rules = []

        for c_dict in condition_combinations:
            # new_effect = rule.effects
            if not self.effects:
                new_effect = Bottom
            else:
                new_effect = reduce(And, map(Var, self.effects))
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
                        if c_dict[f].value == 0:
                            new_effect = Bottom()
                        elif c_dict[f].value == 1:
                            new_effect = new_effect.replace(Var(e), NumericalVar(f, 0))
                        else:
                            new_effect = new_effect.replace(Var(e), reduce(Or, map(lambda v: NumericalVar(f, v), range(0, c_dict[f].value))))
                    case EIncr(f):
                        if bounds[f.compute_repr()] - c_dict[f].value == 0:
                            new_effect = Bottom()
                        elif bounds[f.compute_repr()] - c_dict[f].value <= 1:
                            new_effect = new_effect.replace(Var(e), NumericalVar(f, bounds[f.compute_repr()]))
                        else:
                            new_effect = new_effect.replace(Var(e), reduce(Or, map(lambda v: NumericalVar(f, v), range(c_dict[f].value + 1, bounds[f.compute_repr()] + 1))))
                    case ENEqual(f): new_effect = new_effect.replace(Var(e), NumericalVar(f, c_dict[f].value))
                    case EBAny(f): raise NotImplementedError
                    case ENAny(f): raise NotImplementedError
            # if LTLRule(new_condition, new_effect) not in
            if not new_effect == Bottom():
                new_rules.append(LTLRule(new_condition, new_effect))

        return new_rules


class Sketch:
    rules: list[SketchRule]

    def __init__(self, rules: list[SketchRule]):
        self.rules = rules

    @classmethod
    def from_policy(cls, policy: dlplan.Policy):
        return Sketch([SketchRule.from_dlplan_rule(r) for r in policy.get_rules()])

    def to_ltl(self, bounds: dict[dlplan.Numerical, int]) -> LTLSketch:
        return LTLSketch([nr for r in self.rules for nr in r.to_ltl(bounds)])



