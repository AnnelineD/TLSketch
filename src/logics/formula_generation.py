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

    def follow_rules(self) -> LTLFormula:
        bound = (1, self.n_steps) if self.n_steps else None
        small_bound = (1, self.n_steps//2 + 1) if bound else None
        ces = list(zip(self.conditions, self.effects))
        return Globally(
            (reduce(Or, [e & (Once(c, bound)) for c, e in ces])
             & reduce(Or, [c & (Finally(e, bound)) for c, e in ces]))
            | reduce(Or, [(Once(c, small_bound)) & (Finally(e & ((reduce(Or, [cj & Finally(ej, bound) for cj, ej in ces]) | self.goal)), small_bound)) for c, e in ces])
            | self.goal
        )

    # G((( ∨i (ei ∧ Oci)) ∧ ( ∨i (ci ∧ F ei))) ∨ (∨i(O(ci) ∧ F ei))) → F (goal)
    def rules_followed_then_goal(self) -> LTLFormula:

        return Next(Then(
            self.follow_rules(), Finally(self.goal)
        ))

    def there_exists_a_path(self) -> LTLFormula:    # should be false
        return Next(Not(
            self.follow_rules()
        ))
