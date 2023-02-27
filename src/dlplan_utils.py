from typing import Union

import dlplan


def show_condition(c: dlplan.BaseCondition, representation: str = None) -> str:
    idx = c.get_base_feature().get_index()
    match c.str()[:9]:
        case "(:c_b_pos": return representation if representation else f"b{idx}"
        case "(:c_b_neg": return f"¬{representation}" if representation else f"¬b{idx}"
        case "(:c_n_eq ": return f"{representation}=0" if representation else f"n{idx}=0"
        case "(:c_n_gt ": return f"{representation}>0" if representation else f"n{idx}>0"
        case _: return "invalid"  # TODO raise error


def show_effect(e: dlplan.BaseEffect, representation: str = None) -> str:
    idx = e.get_base_feature().get_index()
    match e.str()[:9]:
        case "(:e_b_pos": return representation if representation else f"b{idx}"
        case "(:e_b_neg": return f"¬{representation}" if representation else f"¬b{idx}"
        case "(:e_b_bot": return f"{representation}?" if representation else f"b{idx}="
        case "(:e_n_inc": return f"{representation}↑" if representation else f"n{idx}↑"
        case "(:e_n_dec": return f"{representation}↓" if representation else f"n{idx}↓"
        case "(:e_n_bot": return f"{representation}?" if representation else f"n{idx}="
        case _: return "invalid"  # TODO raise error

# TODO write tests for the following functions
def show_rule(r: dlplan.Rule) -> str:
    return \
        f"{{{', '.join(list(map(show_condition, r.get_conditions())))}}} -> " \
        f"{{{', '.join(list(map(show_effect, r.get_effects())))}}}"


def show_sketch(s: dlplan.Policy) -> str:
    return '\n'.join([show_rule(r) for r in s.get_rules()])


def repr_feature(f: Union[dlplan.Numerical, dlplan.Boolean]) -> str:
    match f:
        case x if isinstance(x, dlplan.Boolean): return f"b{f.get_index()}"
        case x if isinstance(x, dlplan.Numerical): return f"n{f.get_index()}"
        case _: print("something went wrong with the feature representation")  # TODO raise error


def parse_features(feature_reprs: list[str], factory: dlplan.SyntacticElementFactory) -> tuple[list[dlplan.Boolean], list[dlplan.Numerical]]:
    boolean_features: list[dlplan.Boolean] = [factory.parse_boolean(r, i) for i, r in enumerate(feature_reprs) if r.startswith("b_")]
    numerical_features: list[dlplan.Numerical] = [factory.parse_numerical(r, i) for i, r in enumerate(feature_reprs) if r.startswith("n_")]
    return boolean_features, numerical_features