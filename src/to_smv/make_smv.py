import ctl

from .conversion import *


def to_smv_format(f_domain: DLFeatureTransitionModel, sketch: list[LTLRule], ltl_specs: list[LTLFormula], ctl_specs: list[ctl.CTLFormula]) -> str:
    return "MODULE main\n" \
           + transition_system_to_smv(f_domain.transition_model) + '\n' \
           + features_to_smv(f_domain) + '\n' \
           + rules_to_smv(sketch) + '\n' \
           + "".join(["LTLSPEC " + ltl_to_smv(s) + ";" + '\n' for s in ltl_specs]) \
           + "".join(["CTLSPEC " + ctl_to_smv(s) + ";" + '\n' for s in ctl_specs])
