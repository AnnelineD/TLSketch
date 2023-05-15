import tarski
import dlplan


def transition_system(i: tarski.fstrips.Problem) -> str:
    return f"{i.domain_name}/transition_systems/" \
           f"{'_'.join([c.name for c in i.language.constants()])}_{i.goal.__repr__().replace(' ', '')}.json"
