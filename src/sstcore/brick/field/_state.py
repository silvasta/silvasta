"""
Provide the Bricks for Descriptor Compositions

- Transition from State to State

"""

__all__: list[str] = [
    "TransitionField",
    "StateField",
]

from enum import Enum
from typing import Any

from ...port.attach import Transition
from ._base import ReadField, ResetField, TypedField

type NodeIdentifier = TransitionGraph | str | int


# TODO: cast.arg
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


# REMOVE: 1 class is enough
class TransitionField[T: Enum](TypedField[T], ResetField[T]):
    def __init__(self, *args, transfer: Transition[T], **kwargs) -> None:
        self.transfer: Transition[T] = transfer
        super().__init__(*args, **kwargs)

    def raise_on_transition(self, unit: object, current: T, next: T) -> T:
        cls_attr: str = self._cls_attr_name(unit)
        states = f"({current},{next})"
        raise RuntimeError(f"{cls_attr} failed transfer for {states}")

    # FIX:
    def state_graph_evaluation(
        self, unit: object, current: T, next: T, action: Any = None
    ) -> Any:
        """Implement rigid state-machine rules here"""
        return self.transfer(unit, current, next, action=action)


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

    # FIX:
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
