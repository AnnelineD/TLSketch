import json
import os.path
from typing import Union

import dlplan
from dlplan import State as DLState

from src.logics.conditions_effects import Condition
from src.logics.rules import Sketch, SketchRule

"""
def transition_system(ts: 'TransitionSystem') -> dict:
    return {"init": ts.init, "goals": ts.goals, "graph": ts.graph.adj, "states": ts.states}


def sketch_rule(sr: SketchRule) -> tuple[list[str], list[str]]:
    return list(map(str, sr.conditions)), list(map(str, sr.effects))
"""

"""
def feature_valuations(valuations: dict[str, Union[list[int], list[bool]]], file_path: str):
    with open(file_path, "w") as feature_file:
        json.dump(valuations, feature_file)
"""