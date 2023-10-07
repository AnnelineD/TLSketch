# This file contains functionality to write Sketches as Latex code
# It was used to show generated 'good' sketches in appendix of the thesis dissertation, which was written in Latex

import json

from src.logics.conditions_effects import *
from src.logics.rules import Sketch


def latex_condition(condition: Condition, feature_repr: dict[Feature, str] = None) -> str:
    """
    Write a feature condition in Latex code
    :param condition: a feature condition
    :param feature_repr: Optional. Assigns every feature (as string) to a string that will be used in the latex code to
    represent this feature
    :return: A string that can be used in Latex to show this feature condition
    """
    r = condition.feature if not feature_repr else feature_repr[condition.feature]
    match condition:
        case CPositive(bf): return f"{r}"
        case CNegative(bf): return f"\\neg {r}"
        case CZero(nf): return f"{r} = 0"
        case CGreater(nf): return f"{r}>0"
        case CBAny(_): return ""
        case CNAny(_): return ""
        case _: return "invalid"  # TODO raise error


def latex_effect(e: Effect, feature_repr: dict[Feature, str] = None) -> str:
    """
    Write a feature effect in Latex
    :param e: A feature effect/feature value change
    :param feature_repr: Optional. Assigns every feature (as string) to a string that will be used in the latex code to
    represent this feature
    :return: A string that can be used in Latex to show this feature effect
    """
    r = e.feature if not feature_repr else feature_repr[e.feature]
    match e:
        case EPositive(bf): return f"{r}"
        case ENegative(bf): return f"\\neg {r}"
        case EBEqual(_): return f"{r} \\shorteq"
        case EBAny(bf): return f"{r}?"
        case EIncr(nf): return f"{r} \\uparrow"
        case EDecr(nf): return f"{r} \\downarrow"
        case ENEqual(_): return f"{r}\shorteq"
        case ENAny(nf): return f"{r}?"
        case _: return "invalid"  # TODO raise error


def show_sketch(s: Sketch) -> tuple[list[str], list[str]]:
    """
    Write a sketch into Latex language
    :param s: sketch
    :return: A list of strings that represent the Sketch rules as can be used in Latex, and a list of feature
    definitions, also to use directly in Latex. In these sketch rules features are boolean and numerical features are
    represented as bi and nj respectively, for i, j positive integers. The feature definitions define which feature
    is assigned to which variable (e.g. ni := n_count(...)).
    """
    #make representations
    fs = s.get_features()
    feature_repr = dict()
    n = 0
    b = 0
    for f in fs:
        if f.startswith("n_"):
            feature_repr[f] = f"n_{n}"
            n += 1
        if f.startswith("b_"):
            feature_repr[f] = f"b_{b}"
            b += 1

    s = Sketch([r.simplify() for r in s.rules])

    rules = ["\\{" + ', '.join(latex_condition(c, feature_repr) for c in r.conditions) + "\\}"
             + " \\rightarrow "
             + "\\{" + ", ".join(latex_effect(e, feature_repr) for e in r.effects) + "\\}"
             for r in s.rules]
    underscore = '\\_'
    representations = [f"{n} := \\text{{{f.replace('_', underscore)}}}" for f, n in feature_repr.items()]
    return rules, representations


def one_sketch(s: Sketch) -> str:
    """
    Write one sketch into latex code, including its rules in which features are represented by variables bi and ni for
    positive integers i, and the definition of the variables in terms of description logic descriptions.
    :param s: a sketch
    :return: sketch and feature definitions in Latex code
    """
    rules, representations = show_sketch(s)
    lines = []

    for _ in range(max(len(rules), len(representations))):
        lines.append(f"& {rules.pop() if rules else ''} && {representations.pop() if representations else ''} \\\\")

    return '\n'.join(lines)


def latex_sketches(sketches: list[Sketch]) -> str:
    """
    For a list of sketches, write them all into a Latex "align" environment.
    :param sketches: a list of sketches
    :return: A string containing all sketches that can be used directly into Latex code.
    """
    return "\\begin{align*} \n" \
        + "\n &&& \\\\\\ \n".join(one_sketch(s) for s in sketches) \
        + "\n \\end{align*}"


if __name__ == '__main__':
    """ For each domain used in experiment 1 (generate and verify sketches with one rule and one feature), read all 
    'good' generated sketches from a data file and write them into Latex code. """
    domains = [("blocksworld", 4),
               ("blocksworld-on", 4),
               ("child-snack", 6),
               ("delivery", 5),
               ("gripper-strips", 4),
               ("miconic", 2),
               ("reward-strips", 2),
               ("spanner", 6),
               ("grid-visit-all", 2)]

    for domain, c in domains:
        with open(f"../../generated_final/{domain}/{'_'.join([str(c)]*5)}_180_10000_1/rules_1.json") as f:
            data = json.load(f)
        sketches = [Sketch.deserialize(s) for s in data["working"]]
        print(domain)
        print(latex_sketches(sketches))
        print('\n \n')
