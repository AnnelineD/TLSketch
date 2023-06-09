from dataclasses import dataclass
from typing import Union, Literal

import dlplan
from ltl import Var

Operator = Literal[">", "<", "="]


@dataclass(frozen=True, eq=True)
class FeatureVar(Var):
    data: str
    value: Union[int, bool]
    operator: Operator


@dataclass(frozen=True, eq=True)
class NumericalVar(FeatureVar):
    data: str
    value: int

    def var_show(self) -> str:
        return f"{self.data}{self.operator}{self.value}"


@dataclass(frozen=True, eq=True)
class BooleanVar(FeatureVar):
    data: str
    value: bool
    operator = "="

    def var_show(self) -> str:
        match self.value:
            case True: return f"{self.data}"
            case False: return f"!{self.data}"
