import pynusmv

from ..logics.rules import *
from ..sketch_verification.feature_instance import FeatureInstance
from ..logics.laws import *
from ..to_smv.make_smv import to_smv_format
from ..sketch_verification import logic_translation


def verify_sketch(sketch: Sketch, instance: FeatureInstance, abstract_laws: list[AbstractLaw]) -> bool:
    bounds = instance.get_bounds()
    exp_sketch: ExpandedSketch = sketch.expand(bounds)
    # if instance.init in instance.goal_states:
    #    return True
    if not exp_sketch.rules:
        return False
    laws = [law.expand(exp_sketch.n_rules()) for law in abstract_laws]
    return verification(exp_sketch, instance, laws)


def verification(ltl_sketch, instance, laws) -> bool:
    return check_file(to_smv_format(instance, ltl_sketch), laws)


def check_file(filecontent: str, laws: list[Law]):
    pynusmv.init.init_nusmv()
    try:
        pynusmv.glob.load_from_string(filecontent)
        pynusmv.glob.compute_model()
        fsm = pynusmv.glob.prop_database().master.bddFsm


        for l in laws:
            match l.formula:
                case f if isinstance(f, CTLFormula):
                    if pynusmv.mc.check_ctl_spec(fsm, logic_translation.ctl_to_input(l.formula)) != l.truth:
                        return False
                case f if isinstance(f, LTLFormula):
                    truth = pynusmv.mc.check_ltl_spec(logic_translation.ltl_to_input(l.formula))
                    if truth != l.truth:
                        #print(expl)
                        return False

    finally:
        pynusmv.init.deinit_nusmv()
    return True

