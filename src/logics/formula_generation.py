from functools import reduce

from ltl import *
import ltl


@dataclass
class Once(Unary):
    pass


class Previous(Unary):
    pass


class FormulaGenerator:
    def __init__(self, n_rules: int, n_steps: int = None):
        self.n_rules = n_rules
        self.conditions = [Var(f'c{i}') for i in range(n_rules)]
        self.effects = [Var(f'e{i}') for i in range(n_rules)]
        self.goal = Var('goal')

    # G(V_i c_i V goal V !F(goal))
    def one_condition(self) -> LTLFormula:
        return Globally((reduce(Or, self.conditions)) | self.goal | ~ Finally(self.goal))

    # G((( ∨i (ei ∧ Oci)) ∧ ( ∨i (ci ∧ F ei))) ∨ (∨i(O(ci) ∧ F ei))) → F (goal)
    def rules_followed_then_goal(self) -> LTLFormula:
        return Then(
            Globally(
                reduce(Or, [e & Previous(Once(c)) for c, e in zip(self.conditions, self.effects)])
                | reduce(Or, [c & Next(Finally(e)) for c, e in zip(self.conditions, self.effects)])
                | reduce(Or, [Previous(Once(c)) & Next(Finally(e)) for c, e in zip(self.conditions, self.effects)])
                | self.goal
            ), Finally(self.goal)
        )

    def there_exists_a_path(self) -> LTLFormula:    # should be false
        return Not(
            Globally(
                reduce(Or, [e & Previous(Once(c)) for c, e in zip(self.conditions, self.effects)])
                | reduce(Or, [c & Next(Finally(e)) for c, e in zip(self.conditions, self.effects)])
                | reduce(Or, [Previous(Once(c)) & Next(Finally(e)) for c, e in zip(self.conditions, self.effects)])
                | self.goal
            )
        )
