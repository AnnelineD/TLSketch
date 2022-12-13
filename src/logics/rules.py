from collections import namedtuple
from functools import reduce

from ltl import *

from ..logics.conditions_effects import *
from ..logics.feature_vars import *


Rule = namedtuple("Rule", "conditions effects")


class RuleListRepr(Rule):
    conditions: list[Condition]
    effects: list[list[Effect]]

    def get_condition_features(self) -> set[Feature]:
        return {c.feature for c in self.conditions}

    def get_effect_features(self) -> set[Feature]:
        return {e.feature for le in self.effects for e in le}

    def get_features(self) -> set[Feature]:
        return self.get_condition_features().union(self.get_effect_features())

    def to_ltl(self) -> tuple[LTLFormula, LTLFormula]:
        c_ltl: LTLFormula = reduce(And, map(Var, self.conditions))  # TODO make special kind of var
        e_ltl: LTLFormula = reduce(Or, map(lambda le: reduce(And, map(Var, le)), self.effects))

        return c_ltl, e_ltl

    def show_as_ltl(self):
        c_ltl, e_ltl = self.to_ltl()

        return f"condition: {c_ltl.show()}   effect: {e_ltl.show()}"


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

class ArrowLTLRule(Rule):
    conditions: LTLFormula  # with vars of type Condition
    effects: LTLFormula     # with vars of type Effect

    def __new__(cls, c: LTLFormula, e: LTLFormula):
        self = super(ArrowLTLRule, cls).__new__(cls, c, e)
        for v in c.get_vars():
            assert isinstance(v.data, Condition)
        for v in e.get_vars():
            assert isinstance(v.data, Effect)

        return self

    def get_sub_conditions(self) -> set[Condition]:
        return self.conditions.get_atoms()

    def get_condition_features(self) -> set[Feature]:
        return {c.feature for c in self.get_sub_conditions()}

    def get_sub_effects(self) -> set[Effect]:
        return self.effects.get_atoms()

    def get_effect_features(self) -> set[Feature]:
        return {e.feature for e in self.get_sub_effects()}

    def get_features(self) -> set[Feature]:
        return self.get_condition_features().union(self.get_effect_features())

    def show(self) -> str:
        return f'Condition: {self.conditions.show()}      Effect: {self.effects.show()}'


class LTLSketchAbs:
    rules: list[Rule]
    goal: any

    def __init__(self, rules: list[Rule]):
        self.rules = rules
        self._goal = Var("goal")

        self.alive = Finally(self._goal)  # There exists a path such that finally goal
        self.dead = ~self.alive

    def get_conditions(self):
        return [r.conditions for r in self.rules]

    def rule_should_be_followed(self) -> LTLFormula:
        def rule_statement(s) -> LTLFormula:
            c, e = s
            #return Then(c, Until(~(e & self.dead), e & self.alive))
            return Then(c, Finally(e))

        return reduce(And, map(rule_statement, self.rules))

    def one_condition_must_hold(self) -> LTLFormula:
        return Globally(reduce(Or, self.get_conditions()) | self.dead | self._goal)

    def show(self) -> str:
        return "\n".join(Then(c, Finally(e)).show() for c, e in self.rules)

    def get_formula(self) -> LTLFormula:
        return Then(Globally(self.rule_should_be_followed()), Finally(self._goal)) & self.one_condition_must_hold()


# Instance dependent
class LTLSketch(LTLSketchAbs):
    rules: list[LTLRule]


# Domain but not instance dependent
class ArrowLTLSketch(LTLSketchAbs):
    rules: list[ArrowLTLRule]
    goal = Var("goal")

    def to_LTLSketch(self, feature_bounds: dict[dlplan.Numerical, int]) -> LTLSketch:
        pass  # TODO rearange methods from sketch_to_ltl here


if __name__ == '__main__':
    n = ArrowLTLRule(Var(CGreater('a')), Var(ENAny('a')))
    print(n)

