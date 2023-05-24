import unittest
import src.transition_system as ts


class Cashing(unittest.TestCase):
    def test_transition_system(self):
        instance = ts.tarski.load_instance("../../domains/miconic/domain.pddl", "../../domains/miconic/p-2-2-2.pddl")
        ts.tarski.tarski_to_transition_system(instance)



if __name__ == '__main__':
    unittest.main()
