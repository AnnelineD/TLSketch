import json

from src.logics.conditions_effects import *
from src.logics.rules import Sketch


def latex_condition(condition, feature_repr: dict[str, str] = None) -> str:
    r = condition.feature if not feature_repr else feature_repr[condition.feature]
    match condition:
        case CPositive(bf): return f"{r}"
        case CNegative(bf): return f"\\neg {r}"
        case CZero(nf): return f"{r} = 0"
        case CGreater(nf): return f"{r}>0"
        case CBAny(_): return ""
        case CNAny(_): return ""
        case _: return "invalid"  # TODO raise error


def latex_effect(e, feature_repr: dict[Feature, str] = None):
    r = e.feature.get_index() if not feature_repr else feature_repr[e.feature]
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


def show_sketch(s: Sketch):
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

    print(feature_repr)
    s = Sketch([r.simplify() for r in s.rules])
    for r in s.rules:
        print(r)
    conditions = ', '.join([latex_condition(c, feature_repr) for c in s.rules[0].conditions])
    print("cs", conditions)

    rules = ["\\{" + ', '.join(latex_condition(c, feature_repr) for c in r.conditions) + "\\}"
             + " \\rightarrow "
             + "\\{" + ", ".join(latex_effect(e, feature_repr) for e in r.effects) + "\\}"
             for r in s.rules]
    underscore = '\\_'
    representations = [f"{n} := \\text{{{f.replace('_', underscore)}}}" for f, n in feature_repr.items()]
    return rules, representations


def one_sketch(s: Sketch):
    rules, representations = show_sketch(s)
    lines = []

    for _ in range(max(len(rules), len(representations))):
        lines.append(f"& {rules.pop() if rules else ''} && {representations.pop() if representations else ''} \\\\")

    return '\n'.join(lines)


def latex_sketches(sketches: list[Sketch]):
    return "\\begin{align*} \n" \
        + "\n &&& \\\\\\ \n".join(one_sketch(s) for s in sketches) \
        + "\n \\end{align*}"



if __name__ == '__main__':
    with open("../../generated/blocksworld/4_4_4_4_4_180_10000_1/rules_1_adam.json") as f:
        data = json.load(f)
    sketches = [Sketch.deserialize(s) for s in data["working"]]

    print(latex_sketches(sketches))