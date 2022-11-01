import tarski.search.operations
from tarski.io import PDDLReader

from src.transition_system.tarski_manipulation import *


class TarskiTransitionSystem:
    def __init__(self, problem: TProblem):
        self.problem = problem
        self.states = tarski_transition_model(problem)


def tarski_transition_model(problem: TProblem) -> set[TModel]:
    d = sort_constants(problem.language)
    acts: list[TAction] = get_ground_actions(list(problem.actions.values()), d)

    def recursion(todo: list[TModel], checked: set[TModel]) -> set[TModel]:
        if not todo:
            return checked
        s = todo.pop()
        checked.add(s)

        for a in acts:
            if tarski.search.operations.is_applicable(s, a):
                ns = tarski.search.operations.progress(s, a)
                if ns not in checked:
                    todo.append(ns)

        return recursion(todo, checked)

    return recursion([problem.init], set())


if __name__ == '__main__':
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain('../blocks_4_clear/domain.pddl')
    prb = reader.parse_instance('../blocks_4_clear/p-3-0.pddl')

    print(len(tarski_transition_model(prb)))
