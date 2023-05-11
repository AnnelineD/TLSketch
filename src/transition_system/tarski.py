import tarski.search.operations
from dataclasses import dataclass
from tarski.io import PDDLReader

from .tarski_manipulation import sort_constants, get_ground_actions
from .transition_system import TransitionSystem, StateStr
from .types import *

from src.transition_system.graph import DirectedGraph
import src.file_manager as fm


def load_domain(domain_file: str):
    domain_reader = PDDLReader()
    domain_reader.parse_domain(domain_file)
    return domain_reader.problem


def load_instance(domain_file, instance_file):
    instance_reader = PDDLReader()
    instance_reader.read_problem(domain_file, instance_file)
    return instance_reader.problem

"""
def load_domain_instance(domain_file, instance_file):
    domain_reader = PDDLReader()
    instance_reader = PDDLReader()
    domain_reader.parse_domain(domain_file)
    instance_reader.read_problem(domain_file, instance_file)
    return domain_reader.problem, instance_reader.problem


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
"""

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
                graph.add(idx_s, idx_ns, a.name)
                if ns not in checked:
                    todo.append(ns)

    return states, graph


def tmodel_to_state(tmodel: TModel) -> StateStr:
    return [str(a) for a in tmodel.as_atoms()]


@fm.cashing.cache_to_file("cache/", fm.write.transition_system, fm.read.transition_system, fm.names.transition_system)
def tarski_to_transition_system(instance_problem: TProblem) -> TransitionSystem:
    tstates, graph = construct_graph(instance_problem)
    goal_states: list[int] = calc_goal_states(tstates, instance_problem.goal)
    # add self-loops in goals such that for infinite LTL, we can stay forever in a goal state
    for s in goal_states:
        graph.add(s, s, "goal")

    states = [tmodel_to_state(s) for s in tstates]

    return TransitionSystem(states, graph, tstates.index(instance_problem.init), goal_states)
