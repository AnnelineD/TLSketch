# Define all namer functions for cashing.

import tarski
import dlplan


def transition_system(i: tarski.fstrips.Problem) -> str:
    return f"{i.domain_name}/transition_systems/" \
           f"{i.name}.json"


def transition_system_timer(i: tarski.fstrips.Problem) -> str:
    return f"{i.domain_name}/timers/transition_systems/" \
           f"{i.name}.json"


def feature_vals(dlstates: list[dlplan.core.State], string_features, factory) -> str:
    inst: dlplan.core.InstanceInfo = dlstates[0].get_instance_info()
    return f"{'_'.join([c.get_name() for c in inst.get_objects()])}_{'-'.join(str(a) for a in dlstates[0].get_atom_idxs())}_{repr(inst.get_static_atoms()).replace(' ', '')}.json"


def feature_file(factory, dlstates: list[dlplan.core.State], x1, x2, x3, x4, x5, x6, x7):
    return f"{x1}_{x2}_{x3}_{x4}_{x5}_{x6}_{x7}.json"


"""
def graph(i: tarski.fstrips.Problem) -> str:
    return f"{i.domain_name}/graphs/" \
           f"{'_'.join(c.name for c in i.language.constants())}.json"
"""


def graph_timer(i: tarski.fstrips.Problem) -> str:
    return f"{i.domain_name}/timers/graphs/" \
           f"{'_'.join(c.name for c in i.language.constants())}.json"
