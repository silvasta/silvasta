"""
EXAMPLE - with the idea to build the t-string or even printer machine

...
"""

from enum import Enum

from ._state import StateField


class RenderState(Enum):
    INIT = "init"
    PREP = "prep"
    DRAW = "draw"
    CLEAN = "clean"
    ERROR = "error"


class RenderStateField(StateField[RenderState]):
    """A specialized State Machine for the Render Pipeline"""

    def state_graph_evaluation(
        self, unit: object, current: RenderState, next: RenderState
    ) -> bool:
        raise NotImplementedError("Find proper split with transition!!!")


_VALID_TRANSITIONS = {
    RenderState.INIT: {RenderState.PREP, RenderState.ERROR},
    RenderState.PREP: {RenderState.DRAW, RenderState.ERROR},
    RenderState.DRAW: {RenderState.CLEAN, RenderState.ERROR},
    RenderState.CLEAN: {RenderState.INIT},
    RenderState.ERROR: {RenderState.INIT},  # Requires a reset to recover
}


def transit(unit: object, current: RenderState, next: RenderState, **kwargs):
    return next in _VALID_TRANSITIONS.get(current, set())


class RenderMachine:
    state = RenderStateField(transition=transit)
