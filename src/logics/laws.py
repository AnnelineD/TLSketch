# Law and Abstract Law classes. Laws are Temporal Logic formulas that either should hold or should not hold.

from typing import Callable, Union
from ltl import LTLFormula
from ctl import CTLFormula


class Law:
    """
    Either an LTL or CTL formula that needs to be true or false
    """
    formula: Union[LTLFormula, CTLFormula]
    truth: bool

    def __init__(self, formula: Union[LTLFormula, CTLFormula], truth: bool):
        self.formula = formula
        self.truth = truth


class AbstractLaw:
    """
    A law in which it is still uncertain how many variables there will be
    e.g. an abstract law can be V_i (x_i) which can be expanded into the law x_0 v x_1 v x_2
    """
    law: Callable[[int], Union[LTLFormula, CTLFormula]]     # method that takes an integer n and expands a logical
                                                            # formula such that a formula with n variables is returned
    truth: bool     # whether the law needs to hold or needs to be false

    def __init__(self, law: Callable[[int], Union[LTLFormula, CTLFormula]], truth: bool):
        self.law = law
        self.truth = truth

    def expand(self, n: int) -> Law:
        return Law(self.law(n), self.truth)
