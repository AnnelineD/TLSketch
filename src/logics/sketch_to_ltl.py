from ltl import *
from functools import reduce
from collections import namedtuple

from src.logics.feature_vars import NumericalVar, BooleanVar
from src.logics.rule_representation import *

#  conditions: list[Condition]
#  effects:  list[list[Effect]]
RuleTupleRepr = namedtuple("Rule", "conditions effects")


@dataclass
class LTLRule:
    condition: LTLFormula
    effect: LTLFormula

    def get_condition_features(self) -> set:
        return self.condition.get_atoms()

    def get_effect_features(self) -> set:
        return self.effect.get_atoms()

    def get_features(self) -> set:
        return self.get_condition_features().union(self.get_effect_features())

    def show(self) -> str:
        return f'Condition: {self.condition.show()}      Effect: {self.effect.show()}'


class NumLTL:
    def __init__(self, rules: list[LTLRule]):
        self.rules = rules
        self.conditions = [r.condition for r in self.rules]
        self.goal = Var("goal")
        self.dead = Not(Finally(self.goal))
        self.ltl_conditions = Globally(reduce(Or, self.conditions) | self.dead | self.goal)
        self.reach_goal = Finally(self.goal)

        self.full_rules = [Then(r.condition, Until(Not(r.effect & self.dead), r.effect & Not(self.dead))) for r in self.rules]

    def show(self) -> str:
        return "\n".join(Then(c, Finally(e)).show() for c, e in self.rules)

    def to_formula(self, bounds, goal) -> LTLFormula:
        bounded_rules: list[LTLRule] = fill_in_bounds(self.rules, bounds)


# TODO also fill in effects
def fill_in_bounds(rules: list[LTLRule], bounds: dict[dlplan.Numerical, int]) -> list[LTLRule]:
    def fill_in_condition(condition: LTLFormula) -> list[LTLFormula]:
        vars: set[Condition] = condition.get_atoms()
        conds = [condition]

        for v in vars:
            match v:
                case CGreater(f): conds = [c.replace(Var(v), NumericalVar(f, i)) for i in range(1, bounds[f] + 1) for c in conds]
                case CZero(f): conds = [c.replace(Var(v), NumericalVar(f, 0)) for c in conds]
                case CPositive(f): conds = [c.replace(Var(v), BooleanVar(f, True)) for c in conds]
                case CNegative(f): conds = [c.replace(Var(v), BooleanVar(f, False)) for c in conds]
        return conds

    c_filled_in = [LTLRule(nc, r.effect) for r in rules for nc in fill_in_condition(r.condition)]


def dlplan_rule_to_tuple(rule: dlplan.Rule) -> RuleTupleRepr:
    return RuleTupleRepr([cond_from_dlplan(c) for c in rule.get_conditions()],
                         [[eff_from_dlplan(e) for e in rule.get_effects()]])


def policy_to_rule_tuples(policy: dlplan.Policy) -> list[RuleTupleRepr]:
    merged = list[RuleTupleRepr]()
    for rule in policy.get_rules():
        added = False
        r_conv: RuleTupleRepr = dlplan_rule_to_tuple(rule)
        for m in merged:
            mr = merge_rules(m, r_conv)
            if mr:
                merged.remove(m)
                merged += mr
                added = True
                break

        if not added:
            merged += [r_conv]

    return merged


def to_num_ltl(policy: dlplan.Policy) -> NumLTL:
    ruletups: list[RuleTupleRepr] = policy_to_rule_tuples(policy)

    ltl_rules = list[LTLRule]()
    for r in ruletups:
        c_ltl: LTLFormula = reduce(And, map(Var, r.conditions))  # TODO make special kind of var
        e_ltl: LTLFormula = reduce(Or, map(lambda le: reduce(And, map(Var, le)), r.effects))

        ltl_rules.append(LTLRule(c_ltl, e_ltl))

    return NumLTL(ltl_rules)


def get_condition_features(cs: set[Condition]) -> set[Feature]:
    return {c.feature for c in cs}


def merge_rules(r1: RuleTupleRepr, r2: RuleTupleRepr) -> list[RuleTupleRepr]:
    #  check overlapping
    c1: set[Condition] = set(r1.conditions)
    c2: set[Condition] = set(r2.conditions)
    if c1 == c2:
        return [RuleTupleRepr(r1.conditions, r1.effects + r2.effects)]

    c_intersect: set[Condition] = c1.intersection(c2)

    exclusive_c1 = c1.difference(c_intersect)
    exclusive_c2 = c2.difference(c_intersect)

    excl_fs_1 = get_condition_features(exclusive_c1)
    excl_fs_2 = get_condition_features(exclusive_c2)

    f_intersect = excl_fs_1.intersection(excl_fs_2)

    if not f_intersect:  # if the non overlapping conditions affect different features
        true_c1: set[Condition] = exclusive_c1
        true_c2: set[Condition] = exclusive_c2
        false_c1: set[Condition] = {c.invert() for c in exclusive_c1}
        false_c2: set[Condition] = {c.invert() for c in exclusive_c2}

        merged = []

        #  c1 is true but c2 not
        if true_c2:
            m1 = RuleTupleRepr(c_intersect.union(true_c1).union(false_c2), r1.effects)
            merged.append(m1)

        # c1 if false and c2 true
        if true_c1:
            m2 = RuleTupleRepr(c_intersect.union(false_c1).union(true_c2), r2.effects)
            merged.append(m2)

        # c1 and c2 are true
        m3 = RuleTupleRepr(c_intersect.union(true_c1).union(true_c2), r1.effects + r2.effects)
        merged.append(m3)
        return merged

    return []
