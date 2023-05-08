import ctl

from .conversion import *
from ..logics.rules import LTLSketch
from ..sketch_verification.feature_instance import FeatureInstance

"""
def to_smv_format(f_domain: DLFeatureTransitionModel, sketch: list[LTLRule], ltl_specs: list[LTLFormula], ctl_specs: list[ctl.CTLFormula]) -> str:
    return "MODULE main\n" \
           + transition_system_to_smv(f_domain.transition_model) + '\n' \
           + features_to_smv(f_domain) + '\n' \
           + rules_to_smv(sketch) + '\n' \
           + "".join(["LTLSPEC " + ltl_to_smv(s) + ";" + '\n' for s in ltl_specs]) \
           + "".join(["CTLSPEC " + ctl_to_smv(s) + ";" + '\n' for s in ctl_specs])
"""


def to_smv_format(instance: FeatureInstance, ltl_sketch: LTLSketch) -> str:
       return "MODULE main\n" \
              + graph_to_smv(instance.graph, instance.init) + '\n' \
              + valuations_to_smv(instance.feature_valuations, instance.goal_states) + '\n' \
              + rules_to_smv(ltl_sketch) + '\n'
