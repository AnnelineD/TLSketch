from typing import Union

import dlplan
from dataclasses import dataclass
import dlplan.policy as dlpolicy


Numerical = str
Boolean = str

Feature = Union[Boolean, Numerical]


@dataclass(frozen=True)
class Condition:
    feature: Feature

    def invert(self):  # -> Condition:
        match self:
            case CPositive(bf): return CNegative(bf)
            case CNegative(bf): return CPositive(bf)
            case CGreater(nf): return CZero(nf)
            case CZero(nf): return CGreater(nf)

    def show(self, feature_repr: dict[Feature, str] = None) -> str:
        r = self.feature if not feature_repr else feature_repr[self.feature]
        match self:
            case CPositive(bf): return f"b{r}"
            case CNegative(bf): return f"¬b{r}"
            case CZero(nf): return f"n{r}=0"
            case CGreater(nf): return f"n{r}>0"
            case CBAny(_): return ""
            case CNAny(_): return ""
            case _: return "invalid"  # TODO raise error


def cond_from_dlplan(c: dlpolicy.BaseCondition) -> Condition:
    match str(c)[:9]:
        case "(:c_b_pos": return CPositive(c.get_boolean().compute_repr())
        case "(:c_b_neg": return CNegative(c.get_boolean().compute_repr())
        case "(:c_n_eq ": return CZero(c.get_numerical().compute_repr())
        case "(:c_n_gt ": return CGreater(c.get_numerical().compute_repr())
        case _: return "invalid"  # TODO raise error


@dataclass(frozen=True)
class Effect:
    feature: any

    def show(self, feature_repr: dict[Feature, str] = None):
        r = self.feature.get_index() if not feature_repr else feature_repr[self.feature]
        match self:
            case EPositive(bf): return f"b{r}"
            case ENegative(bf): return f"¬b{r}"
            case EBEqual(_): return f"b{r}="
            case EBAny(bf): return f"b{r}?"
            case EIncr(nf): return f"n{r}↑"
            case EDecr(nf): return f"n{r}↓"
            case ENEqual(_): return f"n{r}="
            case ENAny(nf): return f"n{r}?"
            case _: return "invalid"  # TODO raise error


def eff_from_dlplan(e: dlpolicy.BaseEffect) -> Effect:
    match str(e)[:9]:
        case "(:e_b_pos": return EPositive(e.get_boolean().compute_repr())
        case "(:e_b_neg": return ENegative(e.get_boolean().compute_repr())
        case "(:e_b_bot": return EBEqual(e.get_boolean().compute_repr())
        case "(:e_n_inc": return EIncr(e.get_numerical().compute_repr())
        case "(:e_n_dec": return EDecr(e.get_numerical().compute_repr())
        case "(:e_n_bot": return ENEqual(e.get_numerical().compute_repr())
        case _: return "invalid"  # TODO raise error


@dataclass(frozen=True, eq=True)
class BooleanCondition(Condition):
    feature: Boolean


@dataclass(frozen=True, eq=True)
class NumericalCondition(Condition):
    feature: Numerical


@dataclass(frozen=True, eq=True)
class BooleanEffect(Effect):
    feature: Boolean


@dataclass(frozen=True, eq=True)
class NumericalEffect(Effect):
    feature: Numerical


@dataclass(frozen=True, eq=True)
class CPositive(BooleanCondition):
    pass


@dataclass(frozen=True, eq=True)
class CNegative(BooleanCondition):
    pass


@dataclass(frozen=True, eq=True)
class CBAny(BooleanCondition):
    pass


@dataclass(frozen=True, eq=True)
class CGreater(NumericalCondition):
    pass


@dataclass(frozen=True, eq=True)
class CZero(NumericalCondition):
    pass


@dataclass(frozen=True, eq=True)
class CNAny(NumericalCondition):
    pass


@dataclass(frozen=True, eq=True)
class EPositive(BooleanEffect):
    pass


@dataclass(frozen=True, eq=True)
class ENegative(BooleanEffect):
    pass


@dataclass(frozen=True, eq=True)
class EBEqual(BooleanEffect):
    pass


@dataclass(frozen=True, eq=True)
class EBAny(BooleanEffect):
    pass


@dataclass(frozen=True, eq=True)
class EIncr(NumericalEffect):
    pass


@dataclass(frozen=True, eq=True)
class EDecr(NumericalEffect):
    pass


@dataclass(frozen=True, eq=True)
class ENEqual(NumericalEffect):
    pass


@dataclass(frozen=True, eq=True)
class ENAny(NumericalEffect):
    pass

