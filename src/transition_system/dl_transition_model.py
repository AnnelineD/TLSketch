import dlplan
from dlplan import State as DLState
import copy
from typing import Union

Feature = Union[dlplan.Boolean, dlplan.Numerical]

class DLTransitionModel:
    def __init__(self, instance_info: dlplan.InstanceInfo, states: set[dlplan.State]):
        for s in states:
            assert(s.get_instance_info() == instance_info)
        self.instance_info = instance_info
        self.states = states
        self.b_features: list[dlplan.Boolean] = []
        self.n_features: list[dlplan.Numerical] = []


def eval_feature(feature, states: set[DLState]):  # -> dict[DLState, feature]
    return {s: feature.evaluate(s) for s in states}


def eval_features(features: set[Feature], states: set[DLState]) -> dict[DLState, dict[Feature, any]]:
    return {s: {f: f.evaluate(s) for f in features} for s in states}


def add_feature_propositions(model: DLTransitionModel, feature: Union[dlplan.Boolean, dlplan.Numerical]) -> DLTransitionModel:
    nv: dlplan.VocabularyInfo = copy.deepcopy(model.instance_info.get_vocabulary_info())
    nv.add_predicate(feature.compute_repr(), 1)  # TODO write more beautiful representation for features
    ni = dlplan.InstanceInfo(nv)

    for atom in model.instance_info.get_atoms():
        ni.add_atom(atom.get_predicate(), atom.get_objects())

    new_states = set[dlplan.State]()
    for state in model.states:
        val = feature.evaluate(state)
        n_atom = ni.add_atom(feature.compute_repr(), [str(val)])
        n_state = [ni.get_atom(idx) for idx in state.get_atom_idxs()]
        n_state.append(n_atom)
        print(state)
        print(dlplan.State(ni, n_state))
        print()
        new_states.add(dlplan.State(ni, n_state))

    return DLTransitionModel(ni, new_states)


def add_features(model: DLTransitionModel, features: set[Feature]) -> DLTransitionModel:
    nv: dlplan.VocabularyInfo = copy.deepcopy(model.instance_info.get_vocabulary_info())
    for f in features:
        nv.add_predicate(f.compute_repr(), 1)  # TODO write more beautiful representation for features

    ni = dlplan.InstanceInfo(nv)

    for atom in model.instance_info.get_atoms():
        ni.add_atom(atom.get_predicate(), atom.get_objects())  # add all atoms to the new instance

    feature_vals: dict[DLState, dict[Feature, any]] = eval_features(features, model.states)
    new_states = set[dlplan.State]()
    for state, feature_dict in feature_vals.items():
        new_atoms = list[dlplan.Atom]()
        n_state = [ni.get_atom(idx) for idx in state.get_atom_idxs()]  # copy the state
        for feature, val in feature_dict.items():
            n_atom = ni.add_atom(feature.compute_repr(), [str(val)])
            new_atoms.append(n_atom)

        n_state.extend(new_atoms)  # add feature atoms to the state
        new_states.add(dlplan.State(ni, n_state))
    return DLTransitionModel(ni, new_states)



