import itertools


from logics.rules import *


def fill_in_rule(rule: ArrowLTLRule, bounds: dict[dlplan.Numerical, int]) -> list[LTLRule]:
    # TODO throw error when a numerical feature is missing from the bound dict or if there is a var of wrong type
    features: set[Feature] = rule.get_condition_features()   # Get only the features that are present in conditions or effects
                                                   # We do not need features that are not mentioned in conditions and are unchanged in the effects
    for ef in rule.effects.get_atoms():
        match ef:
            case EBAny(f): features.add(f)  # TODO should be EBEqual
            case NumericalEffect(f): features.add(f)

    options = {f: None for f in features}
    condition_vars: set[Condition] = rule.conditions.get_atoms()

    for v in condition_vars:
        match v:
            case CGreater(f): options[v.feature] = [NumericalVar(f, i) for i in range(1, bounds[f] + 1)]
            case CZero(f): options[v.feature] = [NumericalVar(f, 0)]
            case CPositive(f): options[v.feature] = [BooleanVar(f, True)]
            case CNegative(f): options[v.feature] = [BooleanVar(f, False)]

    # If a feature is not mentioned in the conditions, but it is in the effect we should also know its value
    for f in options:
        if not options[f]:
            match f:
                case x if isinstance(x, dlplan.Numerical): options[f] = [NumericalVar(f, i) for i in range(0, bounds[f] + 1)]
                case x if isinstance(x, dlplan.Boolean): options[f] = [BooleanVar(f, True), BooleanVar(f, False)]
                case _: print("something went wrong while filling in the feature values")        # TODO raise error

    condition_combinations: list[dict[Feature, FeatureVar]] = [dict(zip(options.keys(), values)) for values in itertools.product(*options.values())]

    effect_vars: set[Effect] = rule.effects.get_atoms()
    new_rules = []

    for c_dict in condition_combinations:
        new_effect = rule.effects
        new_condition = rule.conditions
        for v in condition_vars:
            # TODO double check this
            # new_condition = new_condition.replace(Var(v), c_dict[v.feature])
            if len(c_dict) == 0:
                new_condition = Top()
            elif len(c_dict) == 1:
                new_condition = list(c_dict.values())[0]
            else:
                new_condition = reduce(And, c_dict.values())

        for e in effect_vars:
            match e:
                case EPositive(f): new_effect = new_effect.replace(Var(e), BooleanVar(f, True))
                case ENegative(f): new_effect = new_effect.replace(Var(e), BooleanVar(f, False))
                case EBAny(f): new_effect = new_effect.replace(Var(e), BooleanVar(f, c_dict[f].value))  # TODO also the situation where f should keep its value
                case EDecr(f):
                    if c_dict[f].value == 0 or c_dict[f].value == 1:
                        new_effect = new_effect.replace(Var(e), NumericalVar(f, 0))
                    else:
                        new_effect = new_effect.replace(Var(e), reduce(Or, map(lambda v: NumericalVar(f, v), range(0, c_dict[f].value))))
                case EIncr(f):
                    if bounds[f] - c_dict[f].value <= 1:
                        new_effect = new_effect.replace(Var(e), NumericalVar(f, bounds[f]))
                    else:
                        new_effect = new_effect.replace(Var(e), reduce(Or, map(lambda v: NumericalVar(f, v), range(c_dict[f].value + 1, bounds[f] + 1))))
                case ENAny(f): new_effect = new_effect.replace(Var(e), NumericalVar(f, c_dict[f].value))
        # if LTLRule(new_condition, new_effect) not in
        new_rules.append(LTLRule(new_condition, new_effect))

    return new_rules


def fill_in_rules(rules: list[ArrowLTLRule], bounds: dict[dlplan.Numerical, int]) -> list[LTLRule]:
    return [nr for r in rules for nr in fill_in_rule(r, bounds)]


def dlplan_rule_to_tuple(rule: dlplan.Rule) -> RuleListRepr:
    return RuleListRepr([cond_from_dlplan(c) for c in rule.get_conditions()],
                         [[eff_from_dlplan(e) for e in rule.get_effects()]])


def policy_to_rule_tuples(policy: dlplan.Policy) -> list[RuleListRepr]:
    merged = list[RuleListRepr]()
    for rule in policy.get_rules():
        added = False
        r_conv: RuleListRepr = dlplan_rule_to_tuple(rule)
        for m in merged:
            mr = merge_rules(m, r_conv)
            if mr:
                merged.remove(m)
                merged += mr
                added = True
                break

        if not added:
            merged += [r_conv]

    return merged


def policy_to_arrowsketch(policy: dlplan.Policy) -> ArrowLTLSketch:
    ruletups: list[RuleListRepr] = policy_to_rule_tuples(policy)
    mergedtups: list[RuleListRepr] = merge_all_rules(ruletups)

    ltl_rules = list[ArrowLTLRule]()
    for r in mergedtups:
        if not r.conditions:
            c_ltl = Top()
        else:
            c_ltl: LTLFormula = reduce(And, map(Var, r.conditions))  # TODO make special kind of var
        e_ltl: LTLFormula = reduce(Or, map(lambda le: reduce(And, map(Var, le)), r.effects))

        ltl_rules.append(ArrowLTLRule(c_ltl, e_ltl))

    return ArrowLTLSketch(ltl_rules)


def get_condition_features(cs: set[Condition]) -> set[Feature]:
    return {c.feature for c in cs}


def merge_rules(r1: RuleListRepr, r2: RuleListRepr) -> list[RuleListRepr]:
    if r1 == r2:
        return [r1]

    #  check overlapping
    c1: set[Condition] = set(r1.conditions)
    c2: set[Condition] = set(r2.conditions)
    if c1 == c2:
        return [RuleListRepr(r1.conditions, r1.effects + [r for r in r2.effects if r not in r1.effects])]

    c_intersect: set[Condition] = c1.intersection(c2)

    exclusive_c1 = c1.difference(c_intersect)
    exclusive_c2 = c2.difference(c_intersect)

    excl_fs_1 = get_condition_features(exclusive_c1)
    excl_fs_2 = get_condition_features(exclusive_c2)

    f_intersect = excl_fs_1.intersection(excl_fs_2)

    if not f_intersect:  # if the non overlapping conditions affect different features
        true_c1: set[Condition] = exclusive_c1
        true_c2: set[Condition] = exclusive_c2
        false_c1: set[Condition] = {c.invert() for c in exclusive_c1}
        false_c2: set[Condition] = {c.invert() for c in exclusive_c2}

        merged = []

        #  c1 is true but c2 not
        if true_c2:
            m1 = [RuleListRepr(c_intersect.union(true_c1).union({f}), r1.effects) for f in false_c2]
            merged.extend(m1)

        # c1 if false and c2 true
        if true_c1:
            m2 = [RuleListRepr(c_intersect.union(true_c2).union({f}), r2.effects) for f in false_c1]
            merged.extend(m2)

        # c1 and c2 are true
        m3 = RuleListRepr(c_intersect.union(true_c1).union(true_c2), r1.effects + r2.effects)
        merged.append(m3)
        return merged

    return []


def merge_all_rules(rs: list[RuleListRepr]) -> list[RuleListRepr]:
    fts: list[Feature] = []
    for r in rs:
        for f in r.get_condition_features():
            if not f in fts:
                fts.append(f)
    ops = [None]*len(fts)
    for i, f in enumerate(fts):
        match f:
            case x if isinstance(x, dlplan.Boolean): ops[i] = [CPositive(x), CNegative(x)]
            case x if isinstance(x, dlplan.Numerical): ops[i] = [CZero(x), CGreater(x)]
            case _: print("type problem in merge_all_rules")  # TODO raise error

    cs = itertools.product(*ops)
    nrs = []
    for c in cs:
        eff = [e for r in rs if set(r.conditions).issubset(set(c)) for e in r.effects]
        if eff:
            nrs.append(RuleListRepr(set(c), eff))
    return nrs

