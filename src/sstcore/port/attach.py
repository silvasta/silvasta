"""
Define the Shape of Descripors

- Attach attributes to Classes

"""

__all__: list[str] = [
    "DescriptorBase",
    "ReadDescriptor",
    "WriteDescriptor",
    "DeleteDescriptor",
    #
    "Descriptor",
    "CompleteDescriptor",
    #
    "EventDescriptor",
    "ValidateDescriptor",
    "ConfigDescriptor",
    #
    "FieldLoader",
    "LazyDescriptor",
]

from collections.abc import Callable
from typing import Any, Protocol, Self, overload

from .event.emit import Emit


class DescriptorBase(Protocol):
    def __set_name__(self, owner: type, name: str) -> None:
        """Define the Base Contract: Ensure the Name"""


### -- L1 -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class ReadDescriptor[T](DescriptorBase, Protocol):
    @overload
    def __get__(self, unit: None, owner: type) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type) -> T: ...
    def __get__(self, unit: T | None, owner: type | None) -> T | Self:
        """Define the Base Getter Non-Data Descriptor"""


class WriteDescriptor(DescriptorBase, Protocol):
    def __set__(self, unit: Any, value: Any) -> None:
        """Define the Base Setter Data Descriptor"""


class DeleteDescriptor(DescriptorBase, Protocol):
    def __delete__(self, unit: Any) -> None:
        """Define the Base Eraser Data Descriptor"""


### -- L2 -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Descriptor[T](WriteDescriptor, ReadDescriptor[T], Protocol):
    """The Default with Setter and Getter"""


class CompleteDescriptor[T](Descriptor[T], DeleteDescriptor, Protocol):
    """Define the Descriptor equipped with all methods"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Specific
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class EventDescriptor[T](ReadDescriptor[T], Protocol):
    def __init__(self, func: Emit) -> None:
        """Attach (bounded) emit function for Bus call"""

    emit: Emit


class ValidateDescriptor(WriteDescriptor, Protocol):
    def validate(self, unit: object, value: Any) -> Any:
        """Confirm the Value before setting it"""


type FieldLoader[T] = Callable[[Any], T]


class LazyDescriptor[T](Descriptor[T], Protocol):
    def __init__(self, loader: FieldLoader) -> None:
        """Prepare Attribute for load on first call"""

    loader: FieldLoader


class ConfigDescriptor[DataT](Protocol):
    def update(self, **config: DataT) -> Any:
        """Set new values in internal config to change behaviour"""

    config: DataT  # NOTE: check _ExampleConfig in brick.field
