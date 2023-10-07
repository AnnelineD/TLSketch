from typing import Union

import dlplan


def repr_feature(f: Union[dlplan.core.Numerical, dlplan.core.Boolean]) -> str:
    """
    Represent a dlplan feature as a string using its feature index i. Boolean and numerical features are represented
    as bi and ni respectively.
    :param f: Boolean or Numerical feature from the DLPlan library
    :return: String variable that represents the feature
    """
    match f:
        case x if isinstance(x, dlplan.core.Boolean): return f"b{f.get_index()}"
        case x if isinstance(x, dlplan.core.Numerical): return f"n{f.get_index()}"
        case _: print("something went wrong with the feature representation")  # TODO raise error


def parse_features(feature_reprs: list[str], factory: dlplan.core.SyntacticElementFactory) -> tuple[list[dlplan.core.Boolean], list[dlplan.core.Numerical]]:
    """
    Given strings representing features in the syntax of the dlplan library, parse them into dlplan's Boolean or
    Numerical feature objects
    :param feature_reprs: features we want to parse
    :param factory: dlplan factory
    :return: a list of boolean features and a list of numerical features as Boolean and Numerical objects respectively
    """
    boolean_features: list[dlplan.core.Boolean] = [factory.parse_boolean(r) for i, r in enumerate(feature_reprs) if r.startswith("b_")]
    numerical_features: list[dlplan.core.Numerical] = [factory.parse_numerical(r) for i, r in enumerate(feature_reprs) if r.startswith("n_")]
    return boolean_features, numerical_features
