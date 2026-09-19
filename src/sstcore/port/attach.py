"""
Define the Shape of the Field Descriptors

- Attach attributes to Classes
                                                 DependencyLevel[0]
"""

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
    "CallingDescriptor",
    "FieldLoader",
    "EventDescriptor",
    "ConfigDescriptor",
]

from collections.abc import Callable as _Callable
from enum import Enum as _Enum
from typing import Any as _Any
from typing import Protocol as _Protocol
from typing import Self as _Self
from typing import overload as _overload

from .calling import Calling

type Types[T] = type[T] | tuple[type, ...]


class FieldLoader[T](_Callable, _Protocol):
    def __call__(self, _: _Any, /) -> T:
        """Execute with exactly the attached Instance as Input"""


class DescriptorBase(_Protocol):
    """Define the Base Contract: Ensure the Name"""

    public_name: str
    private_name: str

    def __set_name__(self, owner: type, name: str) -> None: ...


#  LINE: -- Level 1 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ReadDescriptor[T](DescriptorBase, _Protocol):
    """Define the Base Getter Non-Data Descriptor"""

    @_overload
    def __get__(self, unit: None, owner: type) -> _Self: ...
    @_overload
    def __get__(self, unit: object, owner: type) -> T: ...
    def __get__(self, unit: T | None, owner: type | None) -> T | _Self: ...
    def read(self, unit: object) -> T: ...


class WriteDescriptor[T](DescriptorBase, _Protocol):
    """Define the Base Setter Data Descriptor"""

    def __set__(self, unit: _Any, value: T) -> None: ...
    def write(self, unit: object, value: T) -> None: ...


class DeleteDescriptor(DescriptorBase, _Protocol):
    """Define the Base Eraser Data Descriptor"""

    def __delete__(self, unit: _Any) -> None: ...
    def remove(self, unit: object) -> None: ...


# NEXT:
class DecoratingField(DescriptorBase, _Protocol):  # MOVE: upwards
    """Define the Descriptor that Decorates"""

    def __init__(
        self, target: _Callable | None = None, *args: _Any, **kwargs: _Any
    ):
        """Insert Initial Strategy or Bind Decorator"""

    def __call__(self, target_func: _Any):
        """Decorate Initial Strategy for Bound Decorator"""


#  LINE: -- Level 2 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# REMOVE: ever needed? maybe to avoid multiple checks? runtime_checkable?
class Descriptor[T](WriteDescriptor[T], ReadDescriptor[T], _Protocol):
    """Standard with Setter and Getter"""


# REMOVE: ever needed? maybe to avoid multiple checks? runtime_checkable?
class CompleteDescriptor[T](Descriptor[T], DeleteDescriptor, _Protocol):
    """Define the Descriptor equipped with all methods"""


#  LINE: -- Specification -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ValidDescriptor[T](WriteDescriptor[T], _Protocol):
    def validate(self, unit: object, value: T) -> T:
        """Confirm the Value while attaching"""


class TypedDescriptor[T](ValidDescriptor[T], _Protocol):
    def __init__(self, types: Types[T]) -> T:
        """Confirm the Type while attaching"""


class LazyDescriptor[T](Descriptor[T], _Protocol):
    def __init__(self, loader: FieldLoader) -> None:
        """Prepare Attribute for load on first call"""

    loader: FieldLoader


# NEXT:
class CallingDescriptor[**In, Out](  # IDEA: split T? In/Out?
    DecoratingField,
    ValidDescriptor[Calling[In, Out]],
    DeleteDescriptor,
    _Protocol,
):
    def switch(self, func: Calling[In, Out]) -> _Self:
        # TODO: check if Self actually helps for something or other options are more valuabl
        """Install new Method LSP conform with Default"""


# NEXT:
class MorphingDescriptor(CallingDescriptor, _Protocol):
    def morph(self, func: Calling) -> _Self:
        # TODO: check if Self actually helps for something or other options are more valuabl
        """Change Method with possible LSP Violation"""


#  LINE: -- State and Transmission -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PolicyEnum(_Enum):  # LATER: improve together with other enums
    """Base for all policy enums, ensuring shared namespace and branding views."""


class PolicyDescriptor[EnumT: PolicyEnum, ResulT: _Any](_Protocol):
    """Govern the Enum including match and dispatch"""

    def match(self, state: EnumT, unit: object) -> ResulT:  # LATER: specify
        """Launch match_func, get override or Raise"""

    def execute(self, unit: object) -> ResulT:  # LATER: specify
        """Apply the injected or overridden Matching-Function"""


class Transition[T](_Protocol):  # LATER: move to state transition
    def __call__(self, unit: object, current: T, next: T, **kwargs) -> _Any:
        """Calculate Actions depending on the State Pair"""


class TransitionDescriptor[T: _Enum](TypedDescriptor[T], _Protocol):
    def __init__(self, *args, transition: Transition, **kwargs) -> None: ...
    def state_graph_evaluation(
        self, unit: object, current: T, next: T
    ) -> _Any:
        """Implement rigid state-machine rules here"""


class StateDescriptor[T: _Enum](
    TransitionDescriptor[T], CompleteDescriptor[T]
):
    """Govern the Lifecycle of the State"""


#  LINE: -- Interactions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _TempEmit[**P, R](_Protocol):
    # TODO: at first usage, update emit with port.event
    def __call__(self, args=P.args, kwargs=P.kwargs) -> None: ...


class EventDescriptor[T](CompleteDescriptor[T], _Protocol):
    emit: _TempEmit

    def __init__(self, func: _TempEmit) -> None:
        """Listen to all Chanels and Message to EventBus"""


class ConfigDescriptor[DataT](_Protocol):
    def update(self, **config: DataT) -> _Any:
        """Modify Configuration and change Behaviour"""

    config: DataT  # NOTE: check _ExampleConfig in brick.field
