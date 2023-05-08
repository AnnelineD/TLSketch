from typing import Callable, Union
from ltl import LTLFormula
from ctl import CTLFormula


class Law:
    formula: Union[LTLFormula, CTLFormula]
    truth: bool

    def __init__(self, formula: Union[LTLFormula, CTLFormula], truth: bool):
        self.formula = formula
        self.truth = truth


class AbstractLaw:
    law: Callable[[int], Union[LTLFormula, CTLFormula]]
    truth: bool

    def __init__(self, law: Callable[[int], Union[LTLFormula, CTLFormula]], truth: bool):
        self.law = law
        self.truth = truth

    def expand(self, n: int) -> Law:
        return Law(self.law(n), self.truth)
