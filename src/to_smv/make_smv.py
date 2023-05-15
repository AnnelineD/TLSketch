import ctl

from .conversion import *
from ..logics.rules import LTLSketch
from ..sketch_verification.feature_instance import FeatureInstance


def to_smv_format(instance: FeatureInstance, ltl_sketch: LTLSketch) -> str:
       return "MODULE main\n" \
              + graph_to_smv(instance.graph, instance.init) + '\n' \
              + valuations_to_smv(instance.feature_valuations, instance.goal_states) + '\n' \
              + rules_to_smv(ltl_sketch) + '\n'
