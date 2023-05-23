import tarski
import dlplan


def transition_system(i: tarski.fstrips.Problem) -> str:
    return f"{i.domain_name}/transition_systems/" \
           f"{'_'.join([c.name for c in i.language.constants()])}_{i.goal.__repr__().replace(' ', '')}.json"


def feature_vals(dlstates: list[dlplan.State], string_features, factory) -> str:
    inst: dlplan.InstanceInfo = dlstates[0].get_instance_info()
    return f"{'_'.join([c.get_name() for c in inst.get_objects()])}_{repr(inst.get_static_atoms()).replace(' ', '')}.json"


def feature_file(factory, x1, x2, x3, x4, x5, x6, x7, x8, dlstates: list[dlplan.State]):
    return f"{x1}_{x2}_{x3}_{x4}_{x5}_{x6}_{x7}_{x8}.json"