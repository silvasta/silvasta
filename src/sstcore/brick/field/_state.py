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


class TransitionField[T: Enum](TypedField[T]):
    def __init__(self, *args, transition: Transition, **kwargs) -> None:
        self.transition: Transition = transition
        super().__init__(*args, **kwargs)

    def raise_on_transition(self, unit: object, current: T, next: T) -> T:
        cls_attr: str = self._cls_attr_name(unit)
        states = f"({current},{next})"
        raise RuntimeError(f"{cls_attr} failed transition for {states}")

    def state_graph_evaluation(self, unit: object, current: T, next: T) -> Any:
        """Implement rigid state-machine rules here"""
        # TODO: return some result
        return self.transition(unit, current, next)


class StateField[T: Enum](TransitionField[T], ReadField, ResetField[T]):
    """State Graph Evaluation and Transition routing"""

    def write(self, unit: object, value: T) -> None:
        current: T = self.read(unit)
        if not self.state_graph_evaluation(unit, current, next=value):
            self.raise_on_transition(unit, current, value)
        super().write(unit, value)

    def remove(self, unit: object) -> None:
        self.write(unit, value=self.default)

    def state_graph_evaluation(self, unit: object, current: T, next: T) -> Any:
        return super().state_graph_evaluation(unit, current, next)
