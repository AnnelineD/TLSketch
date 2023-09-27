# File defining all abstract laws that we will use to verify sketches

from functools import reduce

import ltl
import ctl

from src.logics.laws import AbstractLaw

ltl_conditions = lambda n: [ltl.Var(f'c{i}') for i in range(n)]     # A list of n LTL variables [c0, c1, ... c(n-1)]
ltl_effects = lambda n: [ltl.Var(f'e{i}') for i in range(n)]        # A list of n LTL variables [e0, e1, ... e(n-1)]
rules = lambda n: list(zip(ltl_conditions(n), ltl_effects(n)))      # [(c0, e0), ... (c(n-1), e(n-1)] as LTL vars
ctl_conditions = lambda n: [ctl.Var(f'c{i}') for i in range(n)]     # A list of n CTL variables [c0, c1, ... c(n-1)]
ctl_effects = lambda n: [ctl.Var(f'e{i}') for i in range(n)]        # A list of n CTL variables [e0, e1, ... e(n-1)]
ctl_rules = lambda n: list(zip(ctl_conditions(n), ctl_effects(n)))  # [(c0, e0), ... (c(n-1), e(n-1)] as CTL vars
ltl_goal = ltl.Var('goal')
ctl_goal = ctl.Var('goal')


def ctl_rule_cannot_lead_into_dead(n) -> ctl.CTLFormula:
    """
    A sketch rule should not lead to a dead state.
    :param n: number of (expanded) sktech rules
    :return:
    """
    one_rule = [ctl.AG(ctl.Then(c, ctl.Not(ctl.EX(ctl.EF(ctl.And(e, ctl.Not(ctl.EF(ctl_goal)))))))) for c, e in
                ctl_rules(n)]
    if one_rule:
        return reduce(ctl.And, one_rule)
    else:
        return ctl.Top()


def ctl_rule_can_be_followed(n) -> ctl.CTLFormula:
    """
    For every alive, non-goal state s of the instance, a sketch rule should exist such that its condition is true in s
    and its effect can be reached from s.
    :param n: number of (expanded) sketch rules
    :return:
    """
    follow_in_future = [ctl.And(c, ctl.EX(ctl.EF(ctl.And(e, ctl.EF(ctl_goal))))) for c, e in ctl_rules(n)]
    follow_one_of_rules = reduce(ctl.Or, follow_in_future, ctl.Bottom())

    return ctl.AG(ctl.Or(ctl.Or(follow_one_of_rules, ctl_goal), ctl.Not(ctl.EF(ctl_goal))))


def impl_func(n) -> ltl.LTLFormula:
    """
    Every path starting in the initial state and consisting of a chain of rule applications should eventually reach the
    goal.
    :param n: number of (expanded) sketch rules
    :return:
    """
    apply_rule = reduce(ltl.Or, [ci & ltl.Next(ltl.Finally(ei)) for ci, ei in rules(n)])
    applied_rule = reduce(ltl.Or, [ltl.Previous(ltl.Once(ci)) & ei for ci, ei in rules(n)])
    return ltl.Then(apply_rule & ltl.Globally(ltl.Then(applied_rule, apply_rule | ltl_goal)), ltl.Finally(ltl_goal))


law1 = AbstractLaw(ctl_rule_can_be_followed, True)
law2 = AbstractLaw(ctl_rule_cannot_lead_into_dead, True)

impl_law = AbstractLaw(impl_func, True)


"""     Other laws that we experimented with 
def follow_rules(n) -> ltl.LTLFormula:
    came_from_rule = [e & (ltl.Once(c)) for c, e in rules(n)]
    followed_one_of_rules = reduce(ltl.Or, came_from_rule)
    going_to_follow_rule = reduce(ltl.Or, [c & (ltl.Finally(e)) for c, e in rules(n)])
    follow_rule_or_goal = (reduce(ltl.Or, [cj & ltl.Finally(ej) for cj, ej in rules(n)]) | ltl_goal)

    return ltl.Globally(
        (followed_one_of_rules & going_to_follow_rule)
        | reduce(ltl.Or, [ltl.Once(c) & ltl.Finally(e & (
            follow_rule_or_goal)) for c, e in rules(n)])
        | ltl_goal
    )

# G((( ∨i (ei ∧ Oci)) ∧ ( ∨i (ci ∧ F ei))) ∨ (∨i(O(ci) ∧ F ei))) → F (goal)
def rules_followed_then_goal(n) -> ltl.LTLFormula:
    return ltl.Then(
        follow_rules(n), ltl.Finally(ltl_goal)
    )


def follow_consecutive_rules(n) -> ltl.LTLFormula:
    came_from_rule = [e & (ltl.Once(c)) for c, e in rules(n)]
    followed_one_of_rules = reduce(ltl.Or, came_from_rule)
    going_to_follow_rule = reduce(ltl.Or, [c & (ltl.Finally(e)) for c, e in rules(n)])
    follow_rule_or_goal = (reduce(ltl.Or, [cj & ltl.Finally(ej) for cj, ej in rules(n)]) | ltl_goal)

    return ltl.Then(ltl.Globally(
        (followed_one_of_rules & going_to_follow_rule) | ltl_goal
    ), ltl.Finally(ltl_goal))


def exists(n) -> ltl.LTLFormula:
    came_from_rule = [e & (ltl.Once(c)) for c, e in rules(n)]
    followed_one_of_rules = reduce(ltl.Or, came_from_rule)
    going_to_follow_rule = reduce(ltl.Or, [c & (ltl.Finally(e)) for c, e in rules(n)])
    follow_rule_or_goal = (reduce(ltl.Or, [cj & ltl.Finally(ej) for cj, ej in rules(n)]) | ltl_goal)
    return ltl.Not(ltl.Globally(
        (followed_one_of_rules & going_to_follow_rule) | ltl_goal
    ))

def if_followed_next(n) -> ltl.LTLFormula:
    return ltl.Then(ltl.Globally(ltl.Then(reduce(ltl.Or, [ltl.Once(ci) & ei for ci, ei in rules(n)]),
                                          reduce(ltl.Or, [cj & ltl.Finally(ej) for cj, ej in rules(n)]))),
                    ltl.Finally(ltl_goal))

def simple(n) -> ltl.LTLFormula:  # doesn't work because in most environments there just simply isn't such a path
    return ltl.Then(
        ltl.Globally(ltl.Or(reduce(ltl.Or, [ci & ltl.Next(ltl.Finally(ei)) for ci, ei in rules(n)]), ltl_goal)),
        ltl.Finally(ltl_goal))

def exists_impl_func(n) -> ltl.LTLFormula:
    apply_rule = reduce(ltl.Or, [ci & ltl.Finally(ei) for ci, ei in rules(n)])
    applied_rule = reduce(ltl.Or, [ltl.Once(ci) & ei for ci, ei in rules(n)])
    return ltl.Not(ltl_goal) & ltl.Not(apply_rule & ltl.Globally(ltl.Then(applied_rule, apply_rule | ltl_goal)))
    
# law3 = AbstractLaw(rules_followed_then_goal, True)
# law_test = AbstractLaw(follow_consecutive_rules, True)
# exists = AbstractLaw(exists, False)
# if_followed_next_law = AbstractLaw(if_followed_next, True)
# simple_law = AbstractLaw(simple, True)
# exists_simple_law = AbstractLaw(there_exists_simple, False)
# exists_impl_law = AbstractLaw(exists_impl_func, False)
"""