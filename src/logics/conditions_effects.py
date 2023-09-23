# Classes to represent feature conditions and feature effects (sometimes called feature value changes) used in sketch
# rules

from typing import Union  # Self only supported from python 3.11
from dataclasses import dataclass

import dlplan.policy as dlpolicy

# we represent features as strings to be independent of other libraries
# using strings eases cashing
Numerical = str  # a numerical feature
Boolean = str    # a boolean feature

Feature = Union[Boolean, Numerical]


@dataclass(frozen=True)
class Condition:
    """
    Base class for feature conditions that can be used in the conditions of sketch rules
    """
    feature: Feature

    def invert(self):  # -> Condition:
        match self:
            case CPositive(bf): return CNegative(bf)
            case CNegative(bf): return CPositive(bf)
            case CGreater(nf): return CZero(nf)
            case CZero(nf): return CGreater(nf)

    def show(self, feature_repr: dict[Feature, str] = None) -> str:
        """
        Convert conditions to an easily readable and printable string
        :param feature_repr: For each feature a more readable representation that will be used if provided
        :return: Compact human-readable representation
        """
        # how the feature will be represented
        r = self.feature if not feature_repr else feature_repr[self.feature]
        match self:
            case CPositive(_): return f"b{r}"
            case CNegative(_): return f"¬b{r}"
            case CZero(_): return f"n{r}=0"
            case CGreater(_): return f"n{r}>0"
            case CBAny(_): return ""
            case CNAny(_): return ""
            case _: return "invalid"  # TODO raise error

    @classmethod
    def from_dlplan(cls, c: dlpolicy.BaseCondition):  # -> Self:
        """
        Make Condition object from its representation in the DLPlan library
        :param c: A feature condition in its representation from the DLPlan library
        :return: The feature condition represented in the Condition class
        """
        match str(c)[:9]:
            case "(:c_b_pos": return CPositive(c.get_boolean().compute_repr())
            case "(:c_b_neg": return CNegative(c.get_boolean().compute_repr())
            case "(:c_n_eq ": return CZero(c.get_numerical().compute_repr())
            case "(:c_n_gt ": return CGreater(c.get_numerical().compute_repr())
            case _: return "invalid"  # TODO raise error


@dataclass(frozen=True, eq=True)
class BooleanCondition(Condition):
    """
    Baseclass for boolean feature conditions
    """
    feature: Boolean


@dataclass(frozen=True, eq=True)
class NumericalCondition(Condition):
    """
    Baseclass for numerical feature conditions
    """
    feature: Numerical


@dataclass(frozen=True, eq=True)
class CPositive(BooleanCondition):
    """
    Boolean feature has to be positive (b)
    """
    pass


@dataclass(frozen=True, eq=True)
class CNegative(BooleanCondition):
    """
    Boolean feature has to be negative (¬b)
    """
    pass


@dataclass(frozen=True, eq=True)
class CBAny(BooleanCondition):
    """
    Value of the boolean feature doesn't matter (b?)
    """
    pass


@dataclass(frozen=True, eq=True)
class CGreater(NumericalCondition):
    """
    Numerical feature has to be greater than zero (n>0)
    """
    pass


@dataclass(frozen=True, eq=True)
class CZero(NumericalCondition):
    """
    Numerical feature has to be equal to zero (n=0)
    """
    pass


@dataclass(frozen=True, eq=True)
class CNAny(NumericalCondition):
    """
    Value of the numerical feature doesn't matter (n?)
    """
    pass


@dataclass(frozen=True)
class Effect:
    """
    Base class for a feature effect (aka feature value change) that can be used in the effects of sketch rules
    """
    feature: Feature

    def show(self, feature_repr: dict[Feature, str] = None):
        """
        Convert effects to an easily readable and printable string
        :param feature_repr: For each feature a more readable representation that will be used if provided
        :return: Compact human-readable representation
        """
        r = self.feature if not feature_repr else feature_repr[self.feature]
        match self:
            case EPositive(_): return f"b{r}"
            case ENegative(_): return f"¬b{r}"
            case EBEqual(_): return f"b{r}="
            case EBAny(_): return f"b{r}?"
            case EIncr(_): return f"n{r}↑"
            case EDecr(_): return f"n{r}↓"
            case ENEqual(_): return f"n{r}="
            case ENAny(_): return f"n{r}?"
            case _: return "invalid"  # TODO raise error

    @classmethod
    def from_dlplan(cls, e: dlpolicy.BaseEffect):  # -> Self:
        match str(e)[:9]:
            case "(:e_b_pos": return EPositive(e.get_boolean().compute_repr())
            case "(:e_b_neg": return ENegative(e.get_boolean().compute_repr())
            case "(:e_b_bot": return EBEqual(e.get_boolean().compute_repr())
            case "(:e_n_inc": return EIncr(e.get_numerical().compute_repr())
            case "(:e_n_dec": return EDecr(e.get_numerical().compute_repr())
            case "(:e_n_bot": return ENEqual(e.get_numerical().compute_repr())
            case _: return "invalid"  # TODO raise error


@dataclass(frozen=True, eq=True)
class BooleanEffect(Effect):
    """
    Baseclass for boolean feature effects
    """
    feature: Boolean


@dataclass(frozen=True, eq=True)
class NumericalEffect(Effect):
    """
    Baseclass for numerical feature effects
    """
    feature: Numerical


@dataclass(frozen=True, eq=True)
class EPositive(BooleanEffect):
    """
    Boolean feature has to become positive (b)
    """
    pass


@dataclass(frozen=True, eq=True)
class ENegative(BooleanEffect):
    """
    Boolean feature has to become negative (¬b)
    """
    pass


@dataclass(frozen=True, eq=True)
class EBEqual(BooleanEffect):
    """
    Boolean feature has to keep the same truth value (b=)
    """
    pass


@dataclass(frozen=True, eq=True)
class EBAny(BooleanEffect):
    """
    It doesn't matter how the value of the boolean feature changes (b?)
    """
    pass


@dataclass(frozen=True, eq=True)
class EIncr(NumericalEffect):
    """
    Numerical feature has to increase (n↑)
    """
    pass


@dataclass(frozen=True, eq=True)
class EDecr(NumericalEffect):
    """
    Numerical feature has to decrease (n↓)
    """
    pass


@dataclass(frozen=True, eq=True)
class ENEqual(NumericalEffect):
    """
    Numerical feature has to keep its value (n=)
    """
    pass


@dataclass(frozen=True, eq=True)
class ENAny(NumericalEffect):
    """
    It doesn't matter how the value of the numerical feature changes (b?)
    """
    pass
