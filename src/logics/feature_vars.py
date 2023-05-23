from dataclasses import dataclass
from typing import Union

import dlplan
from ltl import Var


@dataclass(frozen=True, eq=True)
class FeatureVar(Var):
    data: Union[dlplan.Boolean, dlplan.Numerical]
    value: Union[int, bool]


@dataclass(frozen=True, eq=True)
class NumericalVar(FeatureVar):
    data: str
    value: int

    def var_show(self) -> str:
        return f"{self.data}={self.value}"


@dataclass(frozen=True, eq=True)
class BooleanVar(FeatureVar):
    data: str
    value: bool

    def var_show(self) -> str:
        match self.value:
            case True: return f"{self.data}"
            case False: return f"¬{self.data}"
