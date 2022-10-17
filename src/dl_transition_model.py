import dlplan
from dlplan import State as DLState
import copy


class DLTransitionModel:
    def __init__(self, instance_info: dlplan.InstanceInfo, states: set[dlplan.State]):
        for s in states:
            assert(s.get_instance_info() == instance_info)
        self.instance_info = instance_info
        self.states = states
        self.b_features: list[dlplan.Boolean] = []
        self.n_features: list[dlplan.Numerical] = []


def eval_feature(feature, states: list[DLState]):  # -> dict[DLState, feature]
    return {s: feature.evaluate(s) for s in states}


def add_feature_propositions(model: DLTransitionModel, feature) -> DLTransitionModel:
    if isinstance(feature, dlplan.Boolean):
        model.b_features.append(feature)
    if isinstance(feature, dlplan.Numerical):
        model.n_features.append(feature)

    nv: dlplan.VocabularyInfo = copy.deepcopy(model.instance_info.get_vocabulary_info())
    nv.add_predicate(feature.compute_repr(), 1)  # TODO write more beautiful representation for features
    ni = dlplan.InstanceInfo(nv)

    for atom in model.instance_info.get_atoms():
        ni.add_atom(atom.get_predicate(), atom.get_objects())

    new_states = set[dlplan.State]()
    for state in model.states:
        val = feature.evaluate(state)
        n_atom = ni.add_atom(feature.compute_repr(), [str(val)])
        ni.add_atom(n_atom.get_predicate(), n_atom.get_objects())
        n_state = [ni.get_atom(idx) for idx in state.get_atom_idxs()]
        n_state.append(n_atom)
        new_states.add(dlplan.State(ni, n_state))

    return DLTransitionModel(ni, new_states)



