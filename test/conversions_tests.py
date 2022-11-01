import unittest
from src.transition_system.conversions import *


class MyTestCase(unittest.TestCase):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain('../blocks_4_clear/domain.pddl')
    problem = reader.parse_instance('../blocks_4_clear/p-3-0.pddl')
    i = dlinstance_from_tarski(problem.language)

    def test_predicate_conversion(self):
        lan = tarski.fstrips.language("test")
        p = tarski.syntax.predicate.Predicate("test", lan, TSort("obj", lan))
        self.assertEqual(("test", 1), tarski_predicate_to_tuple(p))

    def test_vocabulary_from_tarski(self):
        genv = dlvocab_from_tarski(self.problem.language)

        v = dlplan.VocabularyInfo()
        v.add_predicate("clear", 1)
        v.add_predicate("on-table", 1)
        v.add_predicate("arm-empty", 0)
        v.add_predicate("holding", 1)
        v.add_predicate("on", 2)

        self.assertEqual(v.get_predicates(), genv.get_predicates())

    def test_state_conv(self):
        dlstate: dlplan.State = tmodel_to_dlstate(self.problem.init, self.i)

        dlstate_atoms_as_strs = set([self.i.get_atom(idx).get_name() for idx in dlstate.get_atom_idxs()])
        tstate_atoms_as_strs = set([a.__str__() for a in self.problem.init.as_atoms()])

        self.assertEqual(tstate_atoms_as_strs, dlstate_atoms_as_strs)


if __name__ == '__main__':
    unittest.main()
