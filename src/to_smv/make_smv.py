from .conversion import *
from ..logics.rules import ExpandedSketch
from ..sketch_verification.feature_instance import FeatureInstance


def to_smv_format(instance: FeatureInstance, exp_sketch: ExpandedSketch) -> str:
    """
    Make an SMV specification that defines the transition system of a domain instance, its initial and goal state,
    defines all features of a feature instance and their values in each state of the transition system, and all
    conditions and effects of expanded sketch rules.
    e.g.
    MODULE main
       VAR
         state: {s0, s1, s2, ...};
       ASSIGN
         init(state) := s0;
         next(state) := case
              state = s0: {s1, s2, ...};
              state = s1: {s0};
              state = s2: {s0, ...};
              ...
         esac;
       DEFINE
         n_countc_equalr_primitiveat01r_primitiveat_g01 := case
              state = s0: 2;
              state = s1: 1;
              state = s2: 5;
              ...
         esac;
         b_foo := case
              state = s0: True;
              state = s1: False;
              state = s2: True;
              ...
         esac;
         goal := {s1, s2};
         c0 := n_countc_equalr_primitiveat01r_primitiveat_g01=0;
         e0 := n_countc_equalr_primitiveat01r_primitiveat_g01 > 0;
         c1 := b_foo = True;
         e1 := b_foo = False;
    :param instance: A FeatureInstance object
    :param exp_sketch: An expanded sketch
    :return:  The SMV specification of the transition system of the instance, initial state, goal states, feature values
              in each state and conditions and effects of the expanded sketch.
    """
    return "MODULE main\n" \
        + graph_to_smv(instance.graph, instance.init) + '\n' \
        + valuations_to_smv(instance.feature_valuations, instance.goal_states, exp_sketch.get_features()) + '\n' \
        + rules_to_smv(exp_sketch) + '\n'
