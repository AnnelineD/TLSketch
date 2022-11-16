import tarski.search.operations
from tarski.io import PDDLReader

from src.transition_system.tarski_manipulation import *
from src.transition_system.graph import DirectedGraph


class TarskiTransitionSystem:
    def __init__(self, problem: TProblem):
        self.problem = problem
        self.states, self.graph = tarski_transition_model(problem)


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

