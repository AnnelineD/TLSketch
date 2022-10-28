import dlplan
from dlplan import Policy
from ltl import *
from functools import reduce

policy: Policy


class NumLTL:
    def __init__(self, rules: list[tuple[LTLFormula, LTLFormula]]):
        self.rules = rules
        self.conditions = [r[0] for r in self.rules]


def to_num_ltl(policy: Policy) -> NumLTL:
    # TODO
    # sort policy rules in exclusive groups
    # for each group make cond -> effect ltl statement
        # combinations of options of precondition values

    ltl_rules = list[tuple[LTLFormula, LTLFormula]]()
    # step 1: convert each rule to LTL separately
    for rule in policy.get_rules():
        cs: list[dlplan.BaseCondition] = rule.get_conditions()
        es: list[dlplan.BaseEffect] = rule.get_effects()

        c_ltl: LTLFormula = reduce(And, map(lambda c: Var(c), cs), Top())  # TODO make special kind of var
        e_ltl: LTLFormula = reduce(And, map(lambda e: Var(e), es), Top())

        ltl_rules.append((c_ltl, e_ltl))

    return NumLTL(ltl_rules)



