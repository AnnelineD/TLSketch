import tarski.search.operations
from dataclasses import dataclass
from tarski.io import PDDLReader

from src.utils.timer import timer
from .tarski_manipulation import sort_constants, get_ground_actions
from .transition_system import TransitionSystem, StateStr, GraphSystem
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


def calc_goal_states_from_str(states: list[StateStr], goal) -> list[int]:
    gs = list[int]()
    goal_list = calc_goal_list(goal)
    for i, s in enumerate(states):
        if all(str(g) in s for g in goal_list):
            gs.append(i)
    return gs


@fm.cashing.cache_to_file("../../cache/", lambda x: x.serialize(), GraphSystem.deserialize, fm.names.graph)
@timer("../../cache/", fm.names.graph_timer)
def construct_graph(problem: TProblem) -> GraphSystem:
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

    return GraphSystem([tmodel_to_state(s) for s in states], graph)


def tmodel_to_state(tmodel: TModel) -> StateStr:
    return {str(a) for a in tmodel.as_atoms()}


def compare_states(s1: StateStr, s2: StateStr):
    return set(s1) == set(s2)


@fm.cashing.cache_to_file("../../cache/", lambda x: x.serialize(), TransitionSystem.deserialize, fm.names.transition_system)
@timer("../../cache/", fm.names.transition_system_timer)
def tarski_to_transition_system(instance_problem: TProblem) -> TransitionSystem:
    graph_sys = construct_graph(instance_problem)
    states = graph_sys.states
    graph = graph_sys.graph

    goal_states: list[int] = calc_goal_states_from_str(states, instance_problem.goal)
    # add self-loops in goals such that for infinite LTL, we can stay forever in a goal state
    for s in goal_states:
        graph.add(s, s, "goal")

    return TransitionSystem(states, graph, states.index(tmodel_to_state(instance_problem.init)), goal_states)
