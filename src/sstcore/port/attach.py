"""
Define the Shape of Descripors

- Attach attributes to Classes

"""

from enum import Enum

__all__: list[str] = [
    "DescriptorBase",
    "ReadDescriptor",
    "WriteDescriptor",
    "DeleteDescriptor",
    "Descriptor",
    "CompleteDescriptor",
    #
    "ValidDescriptor",
    "TypedDescriptor",
    "Types",
    "LazyDescriptor",
    "FieldLoader",
    "EventDescriptor",
    "ConfigDescriptor",
]

from collections.abc import Callable
from typing import Any, Protocol, Self, overload

from .event.emit import Emit

type Types[T] = type[T] | tuple[type, ...]
type FieldLoader[T] = Callable[[Any], T]


class DescriptorBase(Protocol):
    """Define the Base Contract: Ensure the Name"""

    public_name: str
    private_name: str

    def __set_name__(self, owner: type, name: str) -> None: ...


### -- L1 -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class ReadDescriptor[T](DescriptorBase, Protocol):
    """Define the Base Getter Non-Data Descriptor"""

    @overload
    def __get__(self, unit: None, owner: type) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type) -> T: ...
    def __get__(self, unit: T | None, owner: type | None) -> T | Self: ...
    def read(self, unit: object) -> T: ...


class WriteDescriptor[T](DescriptorBase, Protocol):
    """Define the Base Setter Data Descriptor"""

    def __set__(self, unit: Any, value: T) -> None: ...
    def write(self, unit: object, value: T) -> None: ...


class DeleteDescriptor(DescriptorBase, Protocol):
    """Define the Base Eraser Data Descriptor"""

    def __delete__(self, unit: Any) -> None: ...
    def remove(self, unit: object) -> None: ...


### -- L2 -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Descriptor[T](WriteDescriptor[T], ReadDescriptor[T], Protocol):
    """Standard with Setter and Getter"""


class CompleteDescriptor[T](Descriptor[T], DeleteDescriptor, Protocol):
    """Define the Descriptor equipped with all methods"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Specific
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class ValidDescriptor[T](WriteDescriptor[T], Protocol):
    def validate(self, unit: object, value: T) -> T:
        """Confirm the Value while attaching"""


class TypedDescriptor[T](ValidDescriptor[T], Protocol):
    def __init__(self, types: Types[T]) -> T:
        """Confirm the Type while attaching"""


class LazyDescriptor[T](Descriptor[T], Protocol):
    def __init__(self, loader: FieldLoader) -> None:
        """Prepare Attribute for load on first call"""

    loader: FieldLoader


class EventDescriptor[T](CompleteDescriptor[T], Protocol):
    emit: Emit

    def __init__(self, func: Emit) -> None:
        """Listen to all Chanels and message to EventBus"""


class ConfigDescriptor[DataT](Protocol):
    def update(self, **config: DataT) -> Any:
        """Change behaviour with new values"""

    config: DataT  # NOTE: check _ExampleConfig in brick.field


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### State
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Transition[T](Protocol):
    def __call__(self, unit: object, current: T, next: T, **kwargs) -> Any:
        """Calculate Actions depending on the State Pair"""


class TransitionDescriptor[T: Enum](TypedDescriptor[T], Protocol):
    def __init__(self, *args, transition: Transition, **kwargs) -> None: ...
    def state_graph_evaluation(self, unit: object, current: T, next: T) -> Any:
        """Implement rigid state-machine rules here"""


class StateDescriptor[T: Enum](TransitionDescriptor[T], CompleteDescriptor[T]):
    """Govern the Lifecycle of the State"""
