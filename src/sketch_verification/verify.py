class Sketch():
    def get_LTL_representation(self, bounds) -> list[LTLRule]:
        ...


class AbstractLaw:
    spec: ...
    truth: ...
    def expand(self):
        ...

class Law:
    spec: ...
    truth: ...

class InstanceInfo():
    self.graph: directedGraph = transitions_sys
    self.init = init
    self.goal_states = goal_states
    self.valuations = valuations

    def get_bounds(self):
        ...

    def _make_instance_smv(self, filename):
        ...


class VerificationContext:
    sketch: Sketch
    instance_info
    constraints = []

    def __init__(self, constraints: list[Contraint]):
        generator = self.get_LTLSketch.n_rules
        self.constraints = ...

    def get_LTL_sketch(self) -> LTLSketch:
        sketch.fill_in_bounds(instance_info.bounds)

    def make_smv_file(self, filename):
        ...


def verify_sketch(sketch: Sketch, instance: InstanceInfo, abstract_laws) -> bool:
    bounds = instance.get_bounds()
    ltl_arrow = toLTLArrow(sketch)
    ltl_sketch = ltl_arrow.fill_in_bounds(bounds)
    laws = [expand(law, ltl_sketch.n_rules) for law in abstract_laws]
    return verification(ltl_sketch, instance, laws)


def verification(ltl_sketch, instance, laws) -> bool:
    filepath = "temp"
    with open(filepath, 'w') as f:
        f.write(to_smv_format(instance, ltl_sketch))
    return check_file(filepath, laws)


def check_file(filepath, laws: list[Law]):
    pynusmv.init.init_nusmv()
    pynusmv.glob.load_from_file(filepath=filepath)
    pynusmv.glob.compute_model()
    fsm = pynusmv.glob.prop_database().master.bddFsm

    for l in law:
        if l.lan == "CTL":
            if pynusmv.mc.check_ctl_spec(fsm, ctl_to_input(l.spec)) != l.truth:
                pynusmv.init.deinit_nusmv()
                return False
        if l.lan == "LTL":
            if pynusmv.mc.check_ltl_spec(ltl_to_input(l.spec)) != l.truth:
                pynusmv.init.deinit_nusmv()
                return False

    pynusmv.init.deinit_nusmv()
    return True



def main():
    for s in sketches:
        for i in instances:
            verify_sketch(sketch, i, laws)