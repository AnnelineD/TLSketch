from functools import reduce

from ltl import *
import ltl


class FormulaGenerator:
    def __init__(self, n_rules: int, n_steps: int = None):
        self.n_rules = n_rules
        self.n_steps = n_steps
        self.conditions = [Var(f'c{i}') for i in range(n_rules)]
        self.effects = [Var(f'e{i}') for i in range(n_rules)]
        self.goal = Var('goal')

    # G(V_i c_i V goal V !F(goal))
    def one_condition(self) -> LTLFormula:
        return Globally((reduce(Or, self.conditions)) | self.goal | ~ Finally(self.goal))

    # G((( ∨i (ei ∧ Oci)) ∧ ( ∨i (ci ∧ F ei))) ∨ (∨i(O(ci) ∧ F ei))) → F (goal)
    def rules_followed_then_goal(self) -> LTLFormula:
        bound = (1, self.n_steps) if self.n_steps else None
        return Then(
            Globally(
                reduce(Or, [e & Previous(Once(c, bound)) for c, e in zip(self.conditions, self.effects)])
                | reduce(Or, [c & Next(Finally(e, bound)) for c, e in zip(self.conditions, self.effects)])
                | reduce(Or, [Previous(Once(c, bound)) & Next(Finally(e, bound)) for c, e in zip(self.conditions, self.effects)])
                | self.goal
            ), Finally(self.goal)
        )

    def there_exists_a_path(self) -> LTLFormula:    # should be false
        bound = (1, self.n_steps) if self.n_steps else None
        return Not(
            Globally(
                reduce(Or, [e & Previous(Once(c, bound)) for c, e in zip(self.conditions, self.effects)])
                | reduce(Or, [c & Next(Finally(e, bound)) for c, e in zip(self.conditions, self.effects)])
                | reduce(Or, [Previous(Once(c)) & Next(Finally(e)) for c, e in zip(self.conditions, self.effects)])
                | self.goal
            )
        )
