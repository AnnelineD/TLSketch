import dlplan

from src.transition_system.conversions import tarski_to_dl_system, dlinstance_from_tarski
from src.transition_system.dl_transition_model import DLTransitionModel
from src.transition_system.tarski_manipulation import get_tarski_domain_and_instance
from src.transition_system.tarski_transition_model import *


class FromFile:
    def __init__(self, domain_file: str, instance_file: str):
        dproblem, iproblem = get_tarski_domain_and_instance(domain_file, instance_file)
        self._dproblem = dproblem
        self._iproblem = iproblem
        self._instance = dlinstance_from_tarski(dproblem.language, iproblem.language)

    def tarski_system(self) -> TarskiTransitionSystem:
        return TarskiTransitionSystem(self._dproblem, self._iproblem)

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


class Gripper(FromFile):
    def __init__(self, instance_file="gripper/p-3-0.pddl"):
        super().__init__("gripper/domain.pddl", instance_file)

    def sketch_0(self):
        return self.read_sketch("drexler_sketches/gripper/gripper_0.txt")

    def sketch_1(self):
        return self.read_sketch("drexler_sketches/gripper/gripper_1.txt")

    def sketch_2(self):
        return self.read_sketch("drexler_sketches/gripper/gripper_2.txt")