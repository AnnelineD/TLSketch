import ctl

from .conversion import *
from ..logics.rules import ExpandedSketch
from ..sketch_verification.feature_instance import FeatureInstance


def to_smv_format(instance: FeatureInstance, exp_sketch: ExpandedSketch) -> str:
       return "MODULE main\n" \
              + graph_to_smv(instance.graph, instance.init) + '\n' \
              + valuations_to_smv(instance.feature_valuations, instance.goal_states, exp_sketch.get_features()) + '\n' \
              + rules_to_smv(exp_sketch) + '\n'
