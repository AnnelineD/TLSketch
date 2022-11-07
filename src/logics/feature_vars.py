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
    data: dlplan.Numerical
    value: int


@dataclass(frozen=True, eq=True)
class BooleanVar(FeatureVar):
    data: dlplan.Boolean
    value: bool
