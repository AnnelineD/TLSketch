import unittest
from src.transition_system.conversions import *


class MyTestCase(unittest.TestCase):
    d_problem, i_problem = get_tarski_domain_and_instance('../blocks_4_clear/domain.pddl', '../blocks_4_clear/p-3-0.pddl')
    i = dlinstance_from_tarski(d_problem.language, i_problem.language)

    domain_pr_2, instance_pr_2 = get_tarski_domain_and_instance('../gripper/domain.pddl', '../gripper/p-3-0.pddl')
    i_2 = dlinstance_from_tarski(domain_pr_2.language, instance_pr_2.language)

    def test_predicate_conversion(self):
        lan = tarski.fstrips.language("test")
        p = tarski.syntax.predicate.Predicate("test", lan, TSort("obj", lan))
        self.assertEqual(("test", 1), tarski_predicate_to_tuple(p))

    def test_vocabulary_from_tarski(self):
        genv = dlvocab_from_tarski(self.d_problem.language, False)

        v = dlplan.VocabularyInfo()
        v.add_predicate("clear", 1)
        v.add_predicate("on-table", 1)
        v.add_predicate("arm-empty", 0)
        v.add_predicate("holding", 1)
        v.add_predicate("on", 2)

        self.assertEqual(v.get_predicates(), genv.get_predicates())

    def test_vocab_constants(self):
        genv = dlvocab_from_tarski(self.domain_pr_2.language, False)

        v = dlplan.VocabularyInfo()
        v.add_predicate("room", 1)
        v.add_predicate("ball", 1)
        v.add_predicate("gripper", 1)
        v.add_predicate("at-robby", 1)
        v.add_predicate("at", 2)
        v.add_predicate("free", 1)
        v.add_predicate("carry", 2)

        v.add_constant("rooma")
        v.add_constant("roomb")

        self.assertEqual(v.get_predicates(), genv.get_predicates())
        self.assertEqual(v.get_constants(), genv.get_constants())  # FIXME should only add domain constants


    def test_state_conv(self):
        dlstate: dlplan.State = tmodel_to_dlstate(self.i_problem.init, self.i)

        dlstate_atoms_as_strs = set([self.i.get_atom(idx).get_name() for idx in dlstate.get_atom_idxs()])
        tstate_atoms_as_strs = set([a.__str__() for a in self.i_problem.init.as_atoms()])

        self.assertEqual(tstate_atoms_as_strs, dlstate_atoms_as_strs)

    def test_system_conv(self):
        t_system = TarskiTransitionSystem(self.d_problem, self.i_problem)
        dl_system = tarski_to_dl_system(t_system)
        self.assertEqual(0, dl_system.initial_state.get_index())
        print(t_system.states)
        print(dl_system.states)


if __name__ == '__main__':
    unittest.main()
