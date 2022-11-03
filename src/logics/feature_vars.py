from dataclasses import dataclass
from typing import Union

import dlplan
from ltl import Var


@dataclass
class FeatureVar(Var):
    data: Union[dlplan.Boolean, dlplan.Numerical]
    value: Union[int, bool]


@dataclass
class NumericalVar(FeatureVar):
    data: dlplan.Numerical
    value: int


@dataclass
class BooleanVar(FeatureVar):
    data: dlplan.Boolean
    value: bool
