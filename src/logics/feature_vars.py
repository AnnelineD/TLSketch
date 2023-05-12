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
    data: dlplan.Boolean
    value: bool

    def var_show(self) -> str:
        idx = self.data.get_index()
        match self.value:
            case True: return f"b{idx}"
            case False: return f"¬b{idx}"
