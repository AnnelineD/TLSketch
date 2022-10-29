import dlplan
import ltl
from dlplan import Policy
from ltl import *
from functools import reduce

policy: Policy


class NumLTL:
    def __init__(self, rules: list[tuple[LTLFormula, LTLFormula]]):
        self.rules = rules
        self.conditions = [r[0] for r in self.rules]


def to_num_ltl(policy: Policy) -> NumLTL:
    curr_precondition_merge: list[tuple[list[dlplan.BaseCondition], list[list[dlplan.BaseEffect]]]] = list()
    new_precondition_merge: list[tuple[list[dlplan.BaseCondition], list[list[dlplan.BaseEffect]]]] = list()
    rules = policy.get_rules()
    for rule in rules:
        if curr_precondition_merge:
            for e, ruleset in enumerate(curr_precondition_merge):
                if rule.get_conditions() == ruleset[0]:
                    ruleset[1].append(rule.get_effects())
                else:
                    new_precondition_merge.append((rule.get_conditions(), rule.get_effects()))
        else:
            new_precondition_merge.append((rule.get_conditions(), [rule.get_effects()]))
        curr_precondition_merge = new_precondition_merge.copy()
    print("yes", new_precondition_merge)

    # TODO merge rules that have independent preconditions
    ltl_rules = list[tuple[LTLFormula, LTLFormula]]()
    # for rule in policy.get_rules():
    #     cs: list[dlplan.BaseCondition] = rule.get_conditions()
    #     es: list[dlplan.BaseEffect] = rule.get_effects()
    for cs, es in new_precondition_merge:
        c_ltl: LTLFormula = reduce(And, map(lambda c: Var(c), cs), Top())  # TODO make special kind of var
        e_ltl: LTLFormula = reduce(Or, map(lambda le: reduce(And, map(lambda e: Var(e), le), Top()), es), Bottom())

        ltl_rules.append((c_ltl, e_ltl))

    return NumLTL(ltl_rules)



