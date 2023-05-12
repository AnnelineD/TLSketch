from functools import reduce

import ltl
import ctl

from src.logics.laws import AbstractLaw


ltl_conditions = lambda n: [ltl.Var(f'c{i}') for i in range(n)]
ltl_effects = lambda n: [ltl.Var(f'e{i}') for i in range(n)]
rules = lambda n: list(zip(ltl_conditions(n), ltl_effects(n)))
ctl_conditions = lambda n: [ctl.Var(f'c{i}') for i in range(n)]
ctl_effects = lambda n: [ctl.Var(f'e{i}') for i in range(n)]
ctl_rules = lambda n: list(zip(ctl_conditions(n), ctl_effects(n)))
ltl_goal = ltl.Var('goal')
ctl_goal = ctl.Var('goal')


def follow_rules(n) -> ltl.LTLFormula:
    return ltl.Globally(
        (reduce(ltl.Or, [e & (ltl.Once(c)) for c, e in rules(n)])
         & reduce(ltl.Or, [c & (ltl.Finally(e)) for c, e in rules(n)]))
        | reduce(ltl.Or, [(ltl.Once(c)) & (ltl.Finally(e & (
                reduce(ltl.Or, [cj & ltl.Finally(ej) for cj, ej in rules(n)]) | ltl_goal))) for c, e in rules(n)])
        | ltl_goal
    )

# G((( ∨i (ei ∧ Oci)) ∧ ( ∨i (ci ∧ F ei))) ∨ (∨i(O(ci) ∧ F ei))) → F (goal)
def rules_followed_then_goal(n) -> ltl.LTLFormula:
    return ltl.Then(
        follow_rules(n), ltl.Finally(ltl_goal)
    )


def ctl_rule_cannot_lead_into_dead(n) -> ctl.CTLFormula:
    one_rule = [ctl.AG(ctl.Then(c, ctl.Not(ctl.EF(ctl.And(e, ctl.Not(ctl.EF(ctl_goal))))))) for c, e in ctl_rules(n)]
    if one_rule: return reduce(ctl.And, one_rule)
    else: return ctl.Top()


def ctl_rule_can_be_followed(n) -> ctl.CTLFormula:
    follow_in_future = [ctl.And(c, ctl.EF(ctl.And(e, ctl.EF(ctl_goal)))) for c, e in ctl_rules(n)]
    follow_one_of_rules = reduce(ctl.Or, follow_in_future, ctl.Bottom())

    return ctl.AG(ctl.Or(ctl.Or(follow_one_of_rules, ctl_goal), ctl.Not(ctl.EF(ctl_goal))))


law1 = AbstractLaw(ctl_rule_can_be_followed, True)
law2 = AbstractLaw(ctl_rule_cannot_lead_into_dead, True)
law3 = AbstractLaw(rules_followed_then_goal, True)