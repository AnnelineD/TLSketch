import dlplan

import src.transition_system as ts


# TODO absolute/relative paths for file reading
base_path = ""

class FromFile:
    def __init__(self, domain_file: str, instance_file: str):
        dproblem = ts.tarski.load_domain(base_path + domain_file)
        iproblem = ts.tarski.load_instance(base_path + domain_file, base_path + instance_file)
        self._dproblem = dproblem
        self._iproblem = iproblem
        self._instance = ts.conversions.dlinstance_from_tarski(dproblem, iproblem)
        self.transition_system = ts.tarski.tarski_to_transition_system(self._iproblem)
        self.dl_states = [ts.dlplan.dlstate_from_state(s, self._instance) for s in self.transition_system.states]
        #self.tarski_system: ts.tarski.TarskiTransitionSystem = ts.tarski.from_instance(self._iproblem)
        #self.dl_system: ts.dlplan.DLTransitionModel = ts.conversions.tarski_to_dl_system(self.tarski_system, self._instance)

    """
    def tarski_system(self) -> ts.tarski.TarskiTransitionSystem:
        return ts.tarski.from_instance(self._iproblem)
    """
    def factory(self) -> dlplan.SyntacticElementFactory:
        return dlplan.SyntacticElementFactory(self._instance.get_vocabulary_info())
    """
    def dl_system(self) -> ts.dlplan.DLTransitionModel:
        return ts.conversions.tarski_to_dl_system(self.tarski_system(), self._instance)
    """

    def read_sketch(self, file) -> dlplan.Policy:
        with open(base_path + file, "r") as f:
            sketch = dlplan.PolicyReader().read("\n".join(f.readlines()), self.factory())
        return sketch


class BlocksOn(FromFile):
    def __init__(self, instance_file="domains/blocks_4_on/p-3-0.pddl"):
        super().__init__("domains/blocks_4_on/domain.pddl", instance_file)

    def sketch_0(self) -> dlplan.Policy:
        """
        {} → {b1}
        {} → {n0↓}
        {¬b0} → {b1=, n0=}
        :return:
        """
        return self.read_sketch("drexler_sketches/blocks-on/blocks-on_0.txt")

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/blocks-on/blocks-on_1.txt")

    def sketch_2(self):
        return self.read_sketch("drexler_sketches/blocks-on/blocks-on_2.txt")

    def sketches(self):
        return [self.sketch_0(), self.sketch_1(), self.sketch_2()]


class BlocksClear(FromFile):
    def __init__(self, instance_file="domains/blocks_4_clear/p-4-100.pddl"):
        super().__init__("domains/blocks_4_clear/domain.pddl", instance_file)

    def sketch_0(self) -> dlplan.Policy:
        return self.read_sketch("drexler_sketches/blocks-clear/blocks-clear_0.txt")

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/blocks-clear/blocks-clear_1.txt")

    def sketch_2(self):
        return self.read_sketch("drexler_sketches/blocks-clear/blocks-clear_2.txt")

    def sketches(self):
        return [self.sketch_0(), self.sketch_1(), self.sketch_2()]


class Gripper(FromFile):
    def __init__(self, instance_file="domains/gripper/p-3-0.pddl"):
        super().__init__("domains/gripper/domain.pddl", instance_file)

    def sketch_0(self):
        return self.read_sketch("drexler_sketches/gripper/gripper_0.txt")

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/gripper/gripper_1.txt")

    def sketch_2(self):
        return self.read_sketch("drexler_sketches/gripper/gripper_2.txt")

    def sketches(self):
        return [self.sketch_0(), self.sketch_1(), self.sketch_2()]


class Childsnack(FromFile):
    def __init__(self, instance_file="domains/childsnack/p-2-1.0-0.0-1-0.pddl"):
        super().__init__("domains/childsnack/domain.pddl", instance_file)

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/childsnack/childsnack_1.txt")

    def sketches(self):
        return [None, self.sketch_1(), None]


class Miconic(FromFile):
    def __init__(self, instance_file="domains/miconic/p-2-2-0.pddl"):
        super().__init__("domains/miconic/domain.pddl", instance_file)

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/miconic/miconic_1.txt")

    def sketch_2(self):
        return self.read_sketch("drexler_sketches/miconic/miconic_2.txt")

    def sketches(self):
        return [None, self.sketch_1(), self.sketch_2()]
