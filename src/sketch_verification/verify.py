import pynusmv

from ..logics.rules import *
from ..sketch_verification.feature_instance import FeatureInstance
from ..logics.laws import *
from ..to_smv.make_smv import to_smv_format
from ..sketch_verification import logic_translation


def verify_sketch(sketch: Sketch, instance: FeatureInstance, abstract_laws: list[AbstractLaw]) -> bool:
    bounds = instance.get_bounds()
    ltl_sketch: LTLSketch = sketch.to_ltl(bounds)
    # if instance.init in instance.goal_states:
    #    return True
    if not ltl_sketch.rules:
        return False
    laws = [law.expand(ltl_sketch.n_rules()) for law in abstract_laws]
    return verification(ltl_sketch, instance, laws)


def verification(ltl_sketch, instance, laws) -> bool:
    filepath = "temp.smv"
    with open(filepath, 'w') as f:
        f.write(to_smv_format(instance, ltl_sketch))
    return check_file(filepath, laws)


def check_file(filepath: str, laws: list[Law]):
    pynusmv.init.init_nusmv()
    pynusmv.glob.load_from_file(filepath=filepath)
    pynusmv.glob.compute_model()
    fsm = pynusmv.glob.prop_database().master.bddFsm

    for l in laws:
        match l.formula:
            case f if isinstance(f, CTLFormula):
                if pynusmv.mc.check_ctl_spec(fsm, logic_translation.ctl_to_input(l.formula)) != l.truth:
                    pynusmv.init.deinit_nusmv()
                    return False
            case f if isinstance(f, LTLFormula):
                if pynusmv.mc.check_ltl_spec(logic_translation.ltl_to_input(l.formula)) != l.truth:
                    pynusmv.init.deinit_nusmv()
                    return False

    pynusmv.init.deinit_nusmv()
    return True

