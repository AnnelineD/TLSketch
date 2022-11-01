from typing import Union

import dlplan
from dataclasses import dataclass

Feature = Union[dlplan.Boolean, dlplan.Numerical]


class Condition:
    feature: Feature

    def invert(self):  # -> Condition:
        match self:
            case CPositive(bf): return CNegative(bf)
            case CNegative(bf): return CPositive(bf)
            case CGreater(nf): return CZero(nf)
            case CZero(nf): return CGreater(nf)

    def show(self, feature_repr: dict[Feature, str] = None):
        r = self.feature.get_index() if not feature_repr else feature_repr[self.feature]
        match self:
            case CPositive(bf):f"b{r}"
            case CNegative(bf): return f"¬b{r}"
            case CZero(nf): return f"n{r}=0"
            case CGreater(nf): return f"n{r}>0"
            case _: return "invalid"  # TODO raise error


def cond_from_dlplan(c: dlplan.BaseCondition) -> Condition:
    match c.str()[:9]:
        case "(:c_b_pos": return CPositive(c.get_base_feature())
        case "(:c_b_neg": return CNegative(c.get_base_feature())
        case "(:c_n_eq ": return CZero(c.get_base_feature())
        case "(:c_n_gt ": return CGreater(c.get_base_feature())
        case _: return "invalid"  # TODO raise error


class Effect:
    feature: any

    def show(self, feature_repr: dict[Feature, str] = None):
        r = self.feature.get_index() if not feature_repr else feature_repr[self.feature]
        match self:
            case EPositive(bf): return f"b{r}"
            case ENegative(bf): return f"¬b{r}"
            case EBAny(bf): return f"{r}?"
            case EIncr(nf): return f"n{r}↑"
            case EDecr(nf): return f"n{r}↓"
            case ENAny(nf): return f"n{r}?"
            case _: return "invalid"  # TODO raise error


def eff_from_dlplan(e: dlplan.BaseEffect) -> Effect:
    match e.str()[:9]:
        case "(:e_b_pos": return EPositive(e.get_base_feature())
        case "(:e_b_neg": return ENegative(e.get_base_feature())
        case "(:e_b_bot": return EBAny(e.get_base_feature())
        case "(:e_n_inc": return EIncr(e.get_base_feature())
        case "(:e_n_dec": return EDecr(e.get_base_feature())
        case "(:e_n_bot": return ENAny(e.get_base_feature())
        case _: return "invalid"  # TODO raise error


@dataclass(frozen=True, eq=True)
class BooleanCondition(Condition):
    feature: dlplan.Boolean


@dataclass(frozen=True, eq=True)
class NumericalCondition(Condition):
    feature: dlplan.Numerical


@dataclass(frozen=True, eq=True)
class BooleanEffect(Effect):
    feature: dlplan.Boolean


@dataclass(frozen=True, eq=True)
class NumericalEffect(Effect):
    feature: dlplan.Numerical


@dataclass(frozen=True, eq=True)
class CPositive(BooleanCondition):
    pass


@dataclass(frozen=True, eq=True)
class CNegative(BooleanCondition):
    pass


@dataclass(frozen=True, eq=True)
class CGreater(NumericalCondition):
    pass


@dataclass(frozen=True, eq=True)
class CZero(NumericalCondition):
    pass


@dataclass(frozen=True, eq=True)
class EPositive(BooleanEffect):
    pass


@dataclass(frozen=True, eq=True)
class ENegative(BooleanEffect):
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
class ENAny(NumericalEffect):
    pass

