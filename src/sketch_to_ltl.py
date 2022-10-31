import dlplan
import ltl
from ltl import *
from functools import reduce
from collections import namedtuple
from src.rule_representation import *


#  conditions: list[Condition]
#  effects:  list[list[Effect]]
RuleTupleRepr = namedtuple("Rule", "conditions effects")


class NumLTL:
    def __init__(self, rules: list[tuple[LTLFormula, LTLFormula]]):
        self.rules = rules
        self.conditions = [r[0] for r in self.rules]


def dlplan_rule_to_tuple(rule: dlplan.Rule) -> RuleTupleRepr:
    return RuleTupleRepr([cond_from_dlplan(c) for c in rule.get_conditions()], [[eff_from_dlplan(e) for e in rule.get_effects()]])


def policy_to_rule_tuples(policy: dlplan.Policy) -> list[RuleTupleRepr]:
    merged = list[RuleTupleRepr]()
    for rule in policy.get_rules():
        added = False
        r_conv: RuleTupleRepr = dlplan_rule_to_tuple(rule)
        for m in merged:
            mr = merge_rules(m, r_conv)
            if mr:
                merged.remove(m)
                merged += [mr]
                added = True
                break

        if not added:
            merged += [r_conv]

    return merged

# FIXME the current test for this function fails
def to_num_ltl(policy: dlplan.Policy) -> NumLTL:
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
    # TODO merge if all not overlapping conditions are exclusive
    ltl_rules = list[tuple[LTLFormula, LTLFormula]]()
    # for rule in policy.get_rules():
    #     cs: list[dlplan.BaseCondition] = rule.get_conditions()
    #     es: list[dlplan.BaseEffect] = rule.get_effects()
    for cs, es in new_precondition_merge:
        c_ltl: LTLFormula = reduce(And, map(lambda c: Var(c), cs), Top())  # TODO make special kind of var
        e_ltl: LTLFormula = reduce(Or, map(lambda le: reduce(And, map(lambda e: Var(e), le), Top()), es), Bottom())

        ltl_rules.append((c_ltl, e_ltl))

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

    if not excl_fs_1:
        print("NOT IMPLEMENTED")
    if not excl_fs_2:
        print("NOT IMPLEMENTED")

    f_intersect = excl_fs_1.intersection(excl_fs_2)

    if not f_intersect:  # if the non overlapping conditions affect different features
        true_c1: set[Condition] = exclusive_c1
        true_c2: set[Condition] = exclusive_c2
        false_c1: set[Condition] = {c.invert() for c in exclusive_c1}
        false_c2: set[Condition] = {c.invert() for c in exclusive_c2}

        #  c1 is true but c2 not
        m1 = RuleTupleRepr(c_intersect.union(true_c1).union(false_c2), r1.effects)

        # c1 if false and c2 true
        m2 = RuleTupleRepr(c_intersect.union(false_c1).union(true_c2), r2.effects)

        # c1 and c2 are true
        m3 = RuleTupleRepr(c_intersect.union(true_c1).union(true_c2), r1.effects + r2.effects)
        return [m1, m2, m3]

    return []

