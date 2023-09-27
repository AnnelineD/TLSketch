# Load domains and instances from PDDL files into taski objects
# Build transition systems from instances

import tarski.search.operations
from tarski.io import PDDLReader

import src.file_manager as fm
from src.transition_system.graph import DirectedGraph
from src.utils.timer import timer
from .tarski_manipulation import sort_constants, get_ground_actions
from .transition_system import TransitionSystem, StateStr, GraphSystem
from .types import *


def load_domain(domain_file: str) -> tarski.fstrips.Problem:
    """
    Parse a planning domain given a PDDL domain file
    :param domain_file: the file path of a PDDL file that contains a planning domain
    :return: a Tarski problem containing the domain information
    """
    domain_reader = PDDLReader()
    domain_reader.parse_domain(domain_file)
    return domain_reader.problem


def load_instance(domain_file, instance_file) -> tarski.fstrips.Problem:
    """
    Parse a planning instance given a domain and an instance of this domain provided as PDDL files
    :param domain_file: the file path of a PDDL file that contains the PDDL description of a planning domain
    :param instance_file: the file path of a PDDL file that contains the PDDL description of an instance of the domain
    :return: a Tarski problem containing the instance information
    """
    instance_reader = PDDLReader()
    instance_reader.read_problem(domain_file, instance_file)
    return instance_reader.problem


def calc_goal_list(goal) -> list[tarski.syntax.Atom]:
    """
    Goals in Tarski problems are represented as logic formulas. This method returns all atoms/predicates present in the
    goal if the goal only uses the "and" connective, otherwise an error is raised.
    E.g. calc_goal_list(clearA 'and' clearB 'and' onAB) = [clearA, clearB, onAB]
    :param goal: An Atom or CompoundFormula from the tarski library with only "and" connectives
    :return: A list of the atoms/predicates that where used in the goal formula
    """
    match goal:
        case tarski.syntax.Atom() as x:
            return [x]
        case tarski.syntax.CompoundFormula() as c:
            match c.connective:
                case tarski.syntax.Connective.And:
                    return [s for s in c.subformulas]   # TODO check that s is an atom and not another connective
                case _:
                    raise NotImplementedError(c.connective)
        case _:
            raise NotImplementedError


def calc_goal_states(states: list[TModel], goal) -> list[int]:
    """
    Find all states in which a goal is true
    :param states: A list of states represented as objects from the tarski Model class
    :param goal: An Atom or CompoundFormula from the tarski library with only "and" connectives
    :return: The indexes of the states in which the goal holds
    """
    gs = list[int]()
    goal_list = calc_goal_list(goal)
    for i, s in enumerate(states):
        if all(g in s.as_atoms() for g in goal_list):
            gs.append(i)
    return gs


def calc_goal_states_from_str(states: list[StateStr], goal) -> list[int]:
    """
    Find all states in which a goal is true
    :param states: A list of states in which each state is represented as a set of strings
    :param goal: An Atom or CompoundFormula from the tarski library with only "and" connectives
    :return: The indexes of the states in which the goal holds
    """
    gs = list[int]()
    goal_list = calc_goal_list(goal)
    for i, s in enumerate(states):
        if all(str(g) in s for g in goal_list):
            gs.append(i)
    return gs


def construct_graph(instance: TProblem) -> GraphSystem:
    """
    Given a domain instance, construct its transition system graph
    :param instance: a Tarski problem class containing a problem instance
    :return: An object containing the transition system graph and the states that label the nodes in the graph
    """
    d = sort_constants(instance.language)
    acts: list[TAction] = get_ground_actions(list(instance.actions.values()), d)

    todo: list[TModel] = [instance.init]
    checked: list[StateStr] = list()
    graph: DirectedGraph = DirectedGraph()
    states: list[StateStr] = list()

    while todo:
        s = todo.pop()
        s_str = tmodel_to_state(s)
        checked.append(s_str)
        if s_str in states:
            idx_s = states.index(s_str)
        else:
            idx_s = graph.grow()
            states.append(s_str)

        has_nbr = False
        for a in acts:
            if tarski.search.operations.is_applicable(s, a):
                has_nbr = True
                ns = tarski.search.operations.progress(s, a)
                ns_str = tmodel_to_state(ns)
                if ns_str in states:
                    idx_ns = states.index(ns_str)
                else:
                    idx_ns = graph.grow()
                    states.append(ns_str)
                graph.add(idx_s, idx_ns, a.name)
                if ns_str not in checked:
                    todo.append(ns)
        if not has_nbr:
            # Add self-loop to all dead-end states such that there are only infinite path in the graph
            graph.add(idx_s, idx_s, "end")

    return GraphSystem([s for s in states], graph)


def tmodel_to_state(tmodel: TModel) -> StateStr:
    """
    Represent a tarski state as a set of strings
    :param tmodel: A Model object from the tarski class which represents a state
    :return: A set of strings in which each string is a proposition, representing the same state
    """
    return {str(a) for a in tmodel.as_atoms()}


""" 
def compare_states(s1: StateStr, s2: StateStr):
    return set(s1) == set(s2)
"""


@fm.cashing.cache_to_file("../../cache/", lambda x: x.serialize(), TransitionSystem.deserialize,
                          fm.names.transition_system)
@timer("../../cache/", fm.names.transition_system_timer)
def tarski_to_transition_system(instance_problem: TProblem) -> TransitionSystem:
    """
    From a domain instance as a Problem object from the tarski library, extract the initial state, goal state,
    transition graph and reachable states.
    :param instance_problem: a domain instance as a Problem object
    :return: a TransitionSystem object containing states, transition graph and initial and goal states
    """
    graph_sys = construct_graph(instance_problem)
    states = graph_sys.states
    graph = graph_sys.graph

    goal_states: list[int] = calc_goal_states_from_str(states, instance_problem.goal)
    # add self-loops in goals such that for infinite LTL, we can stay forever in a goal state
    for s in goal_states:
        graph.add(s, s, "goal")

    return TransitionSystem(states, graph, states.index(tmodel_to_state(instance_problem.init)), goal_states)
