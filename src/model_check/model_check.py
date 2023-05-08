from typing import Iterator

import ltl
import pynusmv

from src.logics.conditions_effects import Condition, Effect
from src.logics.formula_generation import FormulaGenerator
from src.logics.rules import ArrowLTLSketch
from src.logics.sketch_to_ltl import fill_in_rules, list_to_ruletups, ruletups_to_arrowsketch
from src.to_smv.make_smv import to_smv_format


def write_smv(f_domain: DLFeatureTransitionModel, sketch: ArrowLTLSketch, filepath: str = None):
    ltl_rules = fill_in_rules(sketch.rules, f_domain.get_feature_bounds())
    if len(ltl_rules) > 0:
        g = FormulaGenerator(len(ltl_rules))
        with open(filepath, 'w') as f:
            ltl_specs = [g.one_condition(), g.rules_followed_then_goal(), g.there_exists_a_path()]
            ctl_specs = [g.ctl_rule_cannot_lead_into_dead(), g.ctl_rule_can_be_followed()]
            f.write(to_smv_format(f_domain, ltl_rules, ltl_specs, ctl_specs))


def model_check_sketch(f_domain, sketch: ArrowLTLSketch, filepath: str = None) -> bool:
    ltl_rules = fill_in_rules(sketch.rules, f_domain.get_feature_bounds())
    if len(ltl_rules) > 0:
        g = FormulaGenerator(len(ltl_rules))
        with open(filepath, 'w') as f:
            ltl_specs = [g.one_condition(), g.rules_followed_then_goal(), g.there_exists_a_path()]
            ctl_specs = [g.ctl_rule_cannot_lead_into_dead(), g.ctl_rule_can_be_followed()]
            f.write(to_smv_format(f_domain, ltl_rules, ltl_specs, ctl_specs))

    return check_file(filepath)


def model_check_rule(f_domain, rule: tuple[list[Condition], list[Effect]], filepath: str = None) -> bool:
    tups = list_to_ruletups((rule,))
    arrow_rule = ruletups_to_arrowsketch(tups)
    ltl_rules = fill_in_rules(arrow_rule.rules, f_domain.get_feature_bounds())
    if len(ltl_rules) > 0:
        g = FormulaGenerator(len(ltl_rules))
        with open(filepath, 'w') as f:
            ltl_specs = []
            ctl_specs = [g.ctl_rule_cannot_lead_into_dead()]
            f.write(to_smv_format(f_domain, ltl_rules, ltl_specs, ctl_specs))

    return check_file(filepath, [], [False])


def check_file(filepath: str, ltl_outcomes: list[bool] = [True, True, False], ctl_outcomes: list[bool] = [False, True]) -> bool:
    pynusmv.init.init_nusmv()
    pynusmv.glob.load_from_file(filepath=filepath)
    pynusmv.glob.compute_model()
    fsm = pynusmv.glob.prop_database().master.bddFsm
    ltls = [pynusmv.glob.prop_database()[i] for i in [2, 3, 4]]
    ctls = [pynusmv.glob.prop_database()[i] for i in [0, 1]]
    checked = True
    for c, b in zip(ctls, ctl_outcomes):
        if pynusmv.mc.check_ctl_spec(fsm, c.expr) != b:
            checked = False
            break

    if checked:
        for l, b in zip(ltls, ltl_outcomes):
            if pynusmv.mc.check_ltl_spec(l.expr) != b:
                checked = False
                break

    pynusmv.init.deinit_nusmv()
    return checked

"""
def check_file(filepath: str) -> bool:
    pynusmv.init.init_nusmv()
    pynusmv.glob.load_from_file(filepath=filepath)
    pynusmv.glob.compute_model()
    fsm = pynusmv.glob.prop_database().master.bddFsm
    ltls = [pynusmv.glob.prop_database()[i] for i in [2, 3, 4]]
    ctls = [pynusmv.glob.prop_database()[i] for i in [0, 1]]
    # evals = [pynusmv.mc.check_ltl_spec(p.expr) for p in ltls]
    # ctl_evals = [pynusmv.mc.check_ctl_spec(fsm, p.expr) for p in ctls]
    checked = False
    if not pynusmv.mc.check_ctl_spec(fsm, ctls[0].expr):
        if pynusmv.mc.check_ctl_spec(fsm, ctls[1].expr):
            if pynusmv.mc.check_ltl_spec(ltls[0].expr):
                if not pynusmv.mc.check_ltl_spec(ltls[2].expr):
                    if pynusmv.mc.check_ltl_spec(ltls[1].expr):
                        checked = True
    pynusmv.init.deinit_nusmv()
    return checked
    # if evals == [True, True, False] and ctl_evals == [False, True]:
    #     return True

    """

