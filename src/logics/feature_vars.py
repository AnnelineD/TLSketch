# Classes to represent variables based on features that can be used in logical expressions

from dataclasses import dataclass
from typing import Union, Literal
from ltl import Var

Operator = Literal[">", "<", "="]


@dataclass(frozen=True, eq=True)
class FeatureVar(Var):
    """
    A base class for boolean and numerical feature variables
    A feature variable logical statement of the form 'data > n', 'data = n' or 'data < n', with 'data' a feature
    """
    data: str
    value: Union[int, bool]
    operator: Operator


@dataclass(frozen=True, eq=True)
class NumericalVar(FeatureVar):
    """
    A feature variable in which 'data' is a numerical feature
    """
    data: str
    value: int

    def var_show(self) -> str:
        """
        Method to convert feature variables to an easily readable and printable string
        :return: Compact human-readable representation of the form 'data operator value' (e.g. x<5)
        """
        return f"{self.data}{self.operator}{self.value}"


@dataclass(frozen=True, eq=True)
class BooleanVar(FeatureVar):
    """
    A feature variable in which 'data' is a boolean feature
    """
    data: str
    value: bool
    operator = "="   # A boolean feature can only be compared to truth values

    def var_show(self) -> str:
        """
        Method to convert feature variables to an easily readable and printable string
        :return: Compact human-readable representation of the form 'data operator value' (e.g. x or !x)
        """
        match self.value:
            case True: return f"{self.data}"
            case False: return f"!{self.data}"
