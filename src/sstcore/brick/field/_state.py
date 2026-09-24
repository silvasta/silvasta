"""
Provide the Bricks for Descriptor Compositions

- Transition from State to State
                                                 DependencyLevel[2]
"""

# TASK: state for bisect transition? or something similar, at least with Enums

__all__: list[str] = [
    "PolicyField",
    #
    "TransitionField",
    "StateField",
]

from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING, Any

from ...port import attach
from ...port.attach import Transition
from ...port.govern import PolicyEnum
from ._base import ReadField
from ._extend import ResetField, TypedField

type NodeIdentifier = TransitionGraph | str | int


class PolicyFieldEngine[EnumT: PolicyEnum](TypedField[EnumT]):
    """Implement Policy and Execution Logic"""

    def __init__(
        self,
        enum_type: type[EnumT],
        *args,
        match_func: Callable | None = None,  # LATER: specify or sync with port
        **kwargs,
    ):
        self.enum_type: type[EnumT] = enum_type
        self.match_func: Callable | None = match_func
        super().__init__(*args, **kwargs)

    def validate(self, unit: object, value: EnumT) -> EnumT:
        # IDEA: check if there is a valid match_func or override already here?
        # -> otherwise, forward enum_type as types=enum_type in __init__
        raise NotImplementedError

    def match(self, policy: PolicyEnum, unit: object, *args, **kwargs):
        """Inject or Override"""
        # TODO: compare with execute, what is needed??
        if self.match_func:
            return self.match_func(policy, unit, *args, **kwargs)
        raise NotImplementedError(f"No Match Policy defined: {self.enum_type}")

    def execute(self, unit, *args, **kwargs):
        # TODO: why not just self.read? or self._get_val?
        # - if needed, mix ReadField again here
        current_state = getattr(unit, self.private_name)
        return self.match(current_state, unit, *args, **kwargs)


class PolicyField[EnumT: PolicyEnum](PolicyFieldEngine, ReadField):
    """Assemble PolicyEngine with Default Read"""


if TYPE_CHECKING:
    _policy: type[attach.PolicyDescriptor] = PolicyField

#  LINE: -- State (UNCOMPLETED) -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# MOVE: ArgCast
def normalize(node_guess: NodeIdentifier | Any) -> TransitionGraph:
    match node_guess:
        case TransitionGraph():
            return node_guess
        case int() as value:
            return TransitionGraph(value)
        case str() as name:
            return TransitionGraph[name.upper()]
        case _:
            raise ValueError(f"Unrecognized type: {type(node_guess)}")


# MOVE: port, when actually implemented
class TransitionGraph(Enum):
    def path_exisit(self, target: NodeIdentifier) -> bool:
        raise NotImplementedError(t"Path from self -> {target}")

    @classmethod
    def connected(cls, source: NodeIdentifier, target: NodeIdentifier) -> bool:
        source: TransitionGraph = normalize(source)
        target: TransitionGraph = normalize(target)
        return source.path_exisit(target)


def get_action[T](unit: object, current: T, next: T) -> Any:
    raise NotImplementedError


# REMOVE: 1 class is probably enough, or make better split
class TransitionField[T: Enum](TypedField[T], ResetField[T]):
    def __init__(self, *args, transfer: Transition[T], **kwargs) -> None:
        self.transfer: Transition[T] = transfer
        super().__init__(*args, **kwargs)

    def raise_on_transition(self, unit: object, current: T, next: T) -> T:
        cls_attr: str = self.name(unit)
        states = f"({current},{next})"
        raise RuntimeError(f"Failed transfer for {cls_attr}: {states}")

    def state_graph_evaluation(
        self, unit: object, current: T, next: T, action: Any = None
    ) -> Any:  # FIX: later
        """Implement rigid state-machine rules here"""
        return self.transfer(unit, current, next, action=action)


# IMPORTANT: wire this again from scratch, but collect ideas here


class StateField[T: TransitionGraph](TransitionField[T], ReadField):
    """State Graph Evaluation and Transition routing"""

    def write(self, unit: object, value: T) -> None:
        current: T = self.read(unit)

        if not current.path_exisit(target=value):
            self.raise_on_transition(unit, current, value)

        self.state_graph_evaluation(unit, current, next=value)
        super().write(unit, value)

    def remove(self, unit: object) -> None:
        self.write(unit, value=self.default)

    # FIX: later
    def state_graph_evaluation(self, unit: object, current: T, next: T) -> Any:
        action = get_action(unit, current, next)
        result = super().state_graph_evaluation(
            unit, current, next, action=action
        )
        # TODO: more like this
        self.transfer(unit, current, next, action=action)
        match result:
            case 1:
                return
            case 0:
                return
            case _:
                self.raise_on_transition(unit, current, next)


if TYPE_CHECKING:
    _policy: type[attach.StateDescriptor] = StateField
    _policy: type[attach.TransitionDescriptor] = TransitionField


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


"""
EXAMPLE - with the idea to build the t-string or even printer machine

...                                                 ...
"""


class RenderState(Enum):
    INIT = "init"
    PREP = "prep"
    DRAW = "draw"
    CLEAN = "clean"
    ERROR = "error"


class RenderStateField(StateField):
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
