import tarski.search.operations
from tarski.io import PDDLReader

from src.transition_system.tarski_manipulation import *
from src.transition_system.graph import DirectedGraph


class TarskiTransitionSystem:
    def __init__(self, d_problem: TProblem, i_problem: TProblem):
        self.domain = d_problem
        self.instance = i_problem
        self.states, self.graph = tarski_transition_model(i_problem)
        self.goal_states = self._calc_goal_states()

    def _calc_goal_list(self) -> list[tarski.syntax.Atom]:
        match self.instance.goal:
            case tarski.syntax.Atom() as x: return [x]
            case tarski.syntax.CompoundFormula() as c:
                match c.connective:
                    case tarski.syntax.Connective.And:
                        return [s for s in c.subformulas]
                    case _:
                        raise NotImplementedError(c.connective)
            case _: raise NotImplementedError

    def _calc_goal_states(self) -> list[int]:
        gs = list[int]()
        goal_list = self._calc_goal_list()
        for i, s in enumerate(self.states):
            if all(g in s.as_atoms() for g in goal_list):
                gs.append(i)
        return gs



def tarski_transition_model(problem: TProblem) -> tuple[list[TModel], DirectedGraph]:
    d = sort_constants(problem.language)
    acts: list[TAction] = get_ground_actions(list(problem.actions.values()), d)

    todo: list[TModel] = [problem.init]
    checked: list[TModel] = list()
    graph: DirectedGraph = DirectedGraph()
    states: list[TModel] = list()

    while todo:
        s = todo.pop()
        checked.append(s)
        if s in states:
            idx_s = states.index(s)
        else:
            idx_s = graph.grow()
            states.append(s)

        for a in acts:
            if tarski.search.operations.is_applicable(s, a):
                ns = tarski.search.operations.progress(s, a)
                if ns in states:
                    idx_ns = states.index(ns)
                else:
                    idx_ns = graph.grow()
                    states.append(ns)
                graph.add(idx_s, idx_ns, a)
                if ns not in checked:
                    todo.append(ns)

    return states, graph

