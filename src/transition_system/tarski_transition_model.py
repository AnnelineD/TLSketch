import tarski.search.operations
from dataclasses import dataclass
from src.transition_system.tarski_manipulation import *
from src.transition_system.graph import DirectedGraph


@dataclass
class TarskiTransitionSystem:
    states: list[TModel]
    init: TModel    # TODO make int
    goal_states: list[int]
    graph: DirectedGraph


def from_instance(i_problem: TProblem) -> TarskiTransitionSystem:
    states, graph = construct_graph(i_problem)
    goal_states: list[int] = calc_goal_states(states, i_problem.goal)
    for s in goal_states:
        graph.add(s, s, "goal")

    return TarskiTransitionSystem(states, i_problem.init, goal_states, graph)


def calc_goal_list(goal) -> list[tarski.syntax.Atom]:
    match goal:
        case tarski.syntax.Atom() as x: return [x]
        case tarski.syntax.CompoundFormula() as c:
            match c.connective:
                case tarski.syntax.Connective.And:
                    return [s for s in c.subformulas]
                case _:
                    raise NotImplementedError(c.connective)
        case _: raise NotImplementedError


def calc_goal_states(states, goal) -> list[int]:
    gs = list[int]()
    goal_list = calc_goal_list(goal)
    for i, s in enumerate(states):
        if all(g in s.as_atoms() for g in goal_list):
            gs.append(i)
    return gs


def construct_graph(problem: TProblem) -> tuple[list[TModel], DirectedGraph]:
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

