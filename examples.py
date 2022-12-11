import dlplan

from src.transition_system.conversions import tarski_to_dl_system, dlinstance_from_tarski
from src.transition_system.dl_transition_model import DLTransitionModel
from src.transition_system.tarski_manipulation import get_tarski_domain_and_instance
from src.transition_system import tarski_transition_model


# TODO absolute/relative paths for file reading

class FromFile:
    def __init__(self, domain_file: str, instance_file: str):
        dproblem, iproblem = get_tarski_domain_and_instance(domain_file, instance_file)
        self._dproblem = dproblem
        self._iproblem = iproblem
        self._instance = dlinstance_from_tarski(dproblem, iproblem)

    def tarski_system(self) -> tarski_transition_model.TarskiTransitionSystem:
        return tarski_transition_model.from_instance(self._iproblem)

    def factory(self) -> dlplan.SyntacticElementFactory:
        return dlplan.SyntacticElementFactory(self._instance.get_vocabulary_info())

    def dl_system(self) -> DLTransitionModel:
        return tarski_to_dl_system(self.tarski_system(), self._instance)

    def read_sketch(self, file) -> dlplan.Policy:
        with open(file, "r") as f:
            sketch = dlplan.PolicyReader().read("\n".join(f.readlines()), self.factory())
        return sketch


class BlocksOn(FromFile):
    def __init__(self, instance_file="blocks_4_on/p-3-0.pddl"):
        super().__init__("blocks_4_on/domain.pddl", instance_file)

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


class BlocksClear(FromFile):
    def __init__(self, instance_file="blocks_4_clear/p-3-0.pddl"):
        super().__init__("blocks_4_clear/domain.pddl", instance_file)

    def sketch_0(self) -> dlplan.Policy:
        return self.read_sketch("drexler_sketches/blocks-clear/blocks-clear_0.txt")

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/blocks-clear/blocks-clear_1.txt")

    def sketch_2(self):
        return self.read_sketch("drexler_sketches/blocks-clear/blocks-clear_2.txt")


class Gripper(FromFile):
    def __init__(self, instance_file="../../gripper/p-1-0.pddl"):
        super().__init__("../../gripper/domain.pddl", instance_file)

    def sketch_0(self):
        return self.read_sketch("drexler_sketches/gripper/gripper_0.txt")

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/gripper/gripper_1.txt")

    def sketch_2(self):
        return self.read_sketch("drexler_sketches/gripper/gripper_2.txt")


class Childsnack(FromFile):
    def __init__(self, instance_file="childsnack/p-2-1.0-0.0-1-0.pddl"):
        super().__init__("childsnack/domain.pddl", instance_file)

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/childsnack/childsnack_1.txt")

class Miconic(FromFile):
    def __init__(self, instance_file="miconic/p-2-2-0.pddl"):
        super().__init__("miconic/domain.pddl", instance_file)

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/miconic/miconic_1.txt")

    def sketch_2(self):
        return self.read_sketch("drexler_sketches/miconic/miconic_2.txt")