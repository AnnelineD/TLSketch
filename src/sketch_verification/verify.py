import pynusmv

from ..logics.rules import *
from ..sketch_verification.feature_instance import FeatureInstance
from ..logics.laws import *
from ..to_smv.make_smv import to_smv_format
from ..sketch_verification import logic_translation


def verify_sketch(sketch: Sketch, instance: FeatureInstance, abstract_laws: list[AbstractLaw]) -> bool:
    """
    Check whether a sketch adheres to a list of laws on an instance.
    If the sketch doesn't have any rules, False is returned
    :param sketch: The sketch to check
    :param instance: The instance one wants to check on
    :param abstract_laws: The laws that need to hold (or not hold) over the sketches on the instance
    :return: True if all laws hold for the sketch over the transition system of the instance, False if one of the laws
             does not hold
    """
    bounds = instance.get_bounds()
    exp_sketch: ExpandedSketch = sketch.expand(bounds)
    # if instance.init in instance.goal_states:
    #    return True
    if not exp_sketch.rules:
        return False
    laws = [law.expand(exp_sketch.n_rules()) for law in abstract_laws]
    return verification(exp_sketch, instance, laws)


def verification(exp_sketch: ExpandedSketch, instance: FeatureInstance, laws: list[Law]) -> bool:
    """
    Verify whether laws over an expanded sketch hold in the transition system of an instance.
    :param exp_sketch: A sketch expanded over the feature values of the instance.
    :param instance: The instance which transition system is used for model checking
    :param laws: Logic formulas that either need to hold or not over the transition system. Their variables have to be
                 of the form "ci" and "ei" with i < the number of rules in the expanded sketch.
    :return: True if all laws hold for the sketch over the transition system of the instance, False if one of the laws
             does not hold
    """
    return check_file(to_smv_format(instance, exp_sketch), laws)


def check_file(filecontent: str, laws: list[Law]) -> bool:
    """
    Use the NuSMV model checker to check a list of laws over a transition system in SMV format.
    The laws are checked one by one and if a law doesn't hold False is returned.
    :param filecontent: The content of an SMV file as a string
    :param laws: Logic formulas one wants to check to be True or False
    :return: True if all laws hold over the transition system defined in filecontent, False otherwise
    """
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
                        return False

    finally:
        pynusmv.init.deinit_nusmv()
    return True

