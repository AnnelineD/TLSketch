import unittest

import dlplan
import tarski

import src.transition_system as ts
from src.transition_system.dlplan import dlstate_from_state
from src.transition_system.transition_system import StateStr, TransitionSystem


class ConversionTest(unittest.TestCase):

    def setUp(self) -> None:
        domain_dir = "domains/"
        self.d_problem = ts.tarski.load_domain(domain_dir + 'blocks_4_clear/domain.pddl')
        self.i_problem = ts.tarski.load_instance(domain_dir + 'blocks_4_clear/domain.pddl', domain_dir + 'blocks_4_clear/p-3-0.pddl')
        self.i = ts.conversions.dlinstance_from_tarski(self.d_problem, self.i_problem)

        self.domain_pr_2 = ts.tarski.load_domain(domain_dir + 'gripper/domain.pddl')
        self.instance_pr_2 = ts.tarski.load_instance(domain_dir + 'gripper/domain.pddl', domain_dir + 'gripper/p-3-0.pddl')
        i_2 = ts.conversions.dlinstance_from_tarski(self.domain_pr_2, self.instance_pr_2)

    def test_vocabulary_from_tarski(self):
        genv = ts.conversions.dlvocab_from_tarski(self.d_problem.language, False)

        v = dlplan.VocabularyInfo()
        v.add_predicate("clear", 1)
        v.add_predicate("on-table", 1)
        v.add_predicate("arm-empty", 0)
        v.add_predicate("holding", 1)
        v.add_predicate("on", 2)

        self.assertEqual(v.get_predicates(), genv.get_predicates())

    def test_vocab_constants(self):
        genv = ts.conversions.dlvocab_from_tarski(self.domain_pr_2.language, False)

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
        state: StateStr = ts.tarski.tmodel_to_state(self.i_problem.init)
        self.assertEqual({'arm-empty()', 'on-table(b1)', 'on(b3,b1)', 'on(b2,b3)', 'clear(b2)'}, set(state))

        dlstate: dlplan.State = dlstate_from_state(state, self.i)

        dlstate_atoms_as_strs = set([self.i.get_atom(idx).get_name() for idx in dlstate.get_atom_idxs()])
        tstate_atoms_as_strs = set([a.__str__() for a in self.i_problem.init.as_atoms()])

        self.assertEqual(tstate_atoms_as_strs, dlstate_atoms_as_strs)


    def test_instance(self):
        i_blocks = ts.conversions.dlinstance_from_tarski(self.d_problem, self.i_problem)
        self.assertEqual({'clear(b1)', 'clear(b2)', 'clear(b3)', 'on-table(b1)', 'on-table(b2)', 'on-table(b3)', 'arm-empty()', 'holding(b1)', 'holding(b2)', 'holding(b3)', 'on(b1,b2)', 'on(b1,b3)', 'on(b2,b1)', 'on(b2,b3)', 'on(b3,b1)', 'on(b3,b2)'},
                         {a.get_name() for a in i_blocks.get_atoms()})

        # TODO predicates and objects are not matched correctly
        i_gripper = ts.conversions.dlinstance_from_tarski(self.domain_pr_2, self.instance_pr_2)
        self.assertEqual({'room(rooma)', 'room(roomb)', 'room(left)', 'room(right)', 'room(ball1)', 'room(ball2)', 'room(ball3)', 'ball(rooma)', 'ball(roomb)', 'ball(left)', 'ball(right)', 'ball(ball1)', 'ball(ball2)', 'ball(ball3)', 'gripper(rooma)', 'gripper(roomb)', 'gripper(left)', 'gripper(right)', 'gripper(ball1)', 'gripper(ball2)', 'gripper(ball3)', 'at-robby(rooma)', 'at-robby(roomb)', 'at-robby(left)', 'at-robby(right)', 'at-robby(ball1)', 'at-robby(ball2)', 'at-robby(ball3)', 'at(rooma,roomb)', 'at(rooma,left)', 'at(rooma,right)', 'at(rooma,ball1)', 'at(rooma,ball2)', 'at(rooma,ball3)', 'at(roomb,rooma)', 'at(roomb,left)', 'at(roomb,right)', 'at(roomb,ball1)', 'at(roomb,ball2)', 'at(roomb,ball3)', 'at(left,rooma)', 'at(left,roomb)', 'at(left,right)', 'at(left,ball1)', 'at(left,ball2)', 'at(left,ball3)', 'at(right,rooma)', 'at(right,roomb)', 'at(right,left)', 'at(right,ball1)', 'at(right,ball2)', 'at(right,ball3)', 'at(ball1,rooma)', 'at(ball1,roomb)', 'at(ball1,left)', 'at(ball1,right)', 'at(ball1,ball2)', 'at(ball1,ball3)', 'at(ball2,rooma)', 'at(ball2,roomb)', 'at(ball2,left)', 'at(ball2,right)', 'at(ball2,ball1)', 'at(ball2,ball3)', 'at(ball3,rooma)', 'at(ball3,roomb)', 'at(ball3,left)', 'at(ball3,right)', 'at(ball3,ball1)', 'at(ball3,ball2)', 'free(rooma)', 'free(roomb)', 'free(left)', 'free(right)', 'free(ball1)', 'free(ball2)', 'free(ball3)', 'carry(rooma,roomb)', 'carry(rooma,left)', 'carry(rooma,right)', 'carry(rooma,ball1)', 'carry(rooma,ball2)', 'carry(rooma,ball3)', 'carry(roomb,rooma)', 'carry(roomb,left)', 'carry(roomb,right)', 'carry(roomb,ball1)', 'carry(roomb,ball2)', 'carry(roomb,ball3)', 'carry(left,rooma)', 'carry(left,roomb)', 'carry(left,right)', 'carry(left,ball1)', 'carry(left,ball2)', 'carry(left,ball3)', 'carry(right,rooma)', 'carry(right,roomb)', 'carry(right,left)', 'carry(right,ball1)', 'carry(right,ball2)', 'carry(right,ball3)', 'carry(ball1,rooma)', 'carry(ball1,roomb)', 'carry(ball1,left)', 'carry(ball1,right)', 'carry(ball1,ball2)', 'carry(ball1,ball3)', 'carry(ball2,rooma)', 'carry(ball2,roomb)', 'carry(ball2,left)', 'carry(ball2,right)', 'carry(ball2,ball1)', 'carry(ball2,ball3)', 'carry(ball3,rooma)', 'carry(ball3,roomb)', 'carry(ball3,left)', 'carry(ball3,right)', 'carry(ball3,ball1)', 'carry(ball3,ball2)'},
                         {a.get_name() for a in i_gripper.get_atoms()})


    def test_goal(self):
        i_blocks = ts.conversions.dlinstance_from_tarski(self.d_problem, self.i_problem)
        self.assertEqual(['clear_g(b1)'], [a.get_name() for a in i_blocks.get_static_atoms()])

        i_gripper = ts.conversions.dlinstance_from_tarski(self.domain_pr_2, self.instance_pr_2)
        self.assertEqual({'at_g(ball1,roomb)', 'at_g(ball2,roomb)', 'at_g(ball3,roomb)'}, {a.get_name() for a in i_gripper.get_static_atoms()})

    def test_system_conv(self):
        trans_system: TransitionSystem = ts.tarski.tarski_to_transition_system(self.i_problem)
        self.assertEqual(0, trans_system.init)


if __name__ == '__main__':
    unittest.main()
