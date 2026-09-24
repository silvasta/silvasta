"""
Define the Shape of the Field Descriptors

- Attach attributes to Classes
                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "Descriptor",
    "ReadDescriptor",
    "WriteDescriptor",
    "DeleteDescriptor",
    "Descriptor",
    "FullDescriptor",
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
from .govern import PolicyEnum
from .raising import Raiser

type Types[T] = type[T] | tuple[type, ...]  # TODO: tuple[T,???]


class FieldLoader[T](_Callable, _Protocol):
    def __call__(self, _: _Any, /) -> T:
        """Execute with exactly the attached Instance as Input"""


class NamedDescriptor(_Protocol):
    """Define the Base Contract: Ensure the Name"""

    public_name: str
    private_name: str

    def __set_name__(self, owner: type, name: str) -> None: ...


class _DescriptorAccess(_Protocol):
    """IDEA: some querries... mixed into base"""


class _RaisingDescriptor(_Protocol):
    """IDEA: attach Raiser: mix into base"""

    on_error: type[Raiser]


class Descriptor[T](NamedDescriptor, _Protocol):
    """
    Mixed Base Descriptor Definition

    IDEA: mix with query and error

    """


#  LINE: -- Level 1 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ReadDescriptor[T](Descriptor, _Protocol):
    """Define the Base Getter Non-Data Descriptor"""

    @_overload
    def __get__(self, unit: None, owner: type) -> _Self: ...
    @_overload
    def __get__(self, unit: _Any, owner: type) -> T: ...
    def __get__(self, unit: _Any | None, owner: type | None) -> T | _Self: ...
    def read(self, unit: object) -> T: ...


class WriteDescriptor[T](Descriptor, _Protocol):
    """Define the Base Setter Data Descriptor"""

    def __set__(self, unit: _Any, value: T) -> None: ...
    def write(self, unit: object, value: T) -> None: ...


class DeleteDescriptor(Descriptor, _Protocol):
    """Define the Base Eraser Data Descriptor"""

    def __delete__(self, unit: _Any) -> None: ...
    def remove(self, unit: object) -> None: ...


class DecoDescriptor(Descriptor, _Protocol):
    # NEXT: check what and how to parametrize
    """Define the Descriptor that Decorates"""

    def __init__(
        self, target: _Callable | None = None, *args: _Any, **kwargs: _Any
    ):
        """Insert Initial Strategy or Bind Decorator"""

    def __call__(self, target_func: _Any):
        """Decorate Initial Strategy for Bound Decorator"""


class FullDescriptor[T](
    WriteDescriptor[T], ReadDescriptor[T], DeleteDescriptor, _Protocol
):
    """Define the Descriptor equipped with all methods"""


#  LINE: -- Extensions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ValidDescriptor[T](WriteDescriptor[T], _Protocol):
    def validate(self, unit: object, value: T) -> T:
        """Confirm the Value while attaching"""


class TypedDescriptor[T](ValidDescriptor[T], _Protocol):
    def __init__(self, types: Types[T]) -> T:
        """Confirm the Type while attaching"""


#  LINE: -- Combinations -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LazyDescriptor[T](Descriptor[T], _Protocol):
    def __init__(self, loader: FieldLoader) -> None:
        """Prepare Attribute for load on first call"""

    loader: FieldLoader


#  LINE: -- Strategy -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# NEXT: check what needed / required
class CallingDescriptor[**In, Out](
    DecoDescriptor,
    ValidDescriptor[Calling[In, Out]],
    ReadDescriptor[Calling[In, Out]],
    DeleteDescriptor,  # TODO: needed/desired? del Cls.method -> default? why not?
    _Protocol,
):
    """Switch Callable Attribute (Method) with enforced Rules"""

    def switch(self, func: Calling[In, Out]) -> _Self:
        # TODO: check if Self useful or other returns are more valuable
        """Install new LSP conform Method"""


# NEXT: check what needed / required
class MorphingDescriptor(CallingDescriptor, _Protocol):
    """Switch Callable Attribute (Method) with less Rules"""

    def morph(self, func: Calling) -> _Self:
        # TODO: check if Self useful or other returns are more valuable
        """Install new Method with possible LSP Violation"""


#  LINE: -- State and Transmission -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PolicyDescriptor[EnumT: PolicyEnum](_Protocol):
    """Govern the Enum including match and dispatch"""

    def match(self, state: EnumT, unit: object):  # LATER: specify
        """Launch match_func, get override or Raise"""


class Transition[T](_Protocol):  # LATER: move to state transition
    def __call__(self, unit: object, current: T, next: T, **kwargs) -> _Any:
        """Calculate Actions depending on the State Pair"""


class TransitionDescriptor[T: _Enum](TypedDescriptor[T], _Protocol):
    def __init__(self, *args, transition: Transition, **kwargs) -> None: ...
    def state_graph_evaluation(
        self, unit: object, current: T, next: T
    ) -> _Any:
        """Implement rigid state-machine rules here"""


class StateDescriptor[T: _Enum](TransitionDescriptor[T], FullDescriptor[T]):
    """Govern the Lifecycle of the State"""


#  LINE: -- Interactions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _TempEmit[**P, R](_Protocol):
    def __call__(self, args=P.args, kwargs=P.kwargs) -> None:
        """# TODO: at first usage, update emit with port.event"""


class EventDescriptor[T](_Protocol):
    emit: _TempEmit

    def __init__(self, func: _TempEmit) -> None:
        """Listen to all Chanels and Message to EventBus"""


class ConfigDescriptor[DataT](_Protocol):
    def update(self, **config: DataT) -> _Any:
        """Modify Configuration and change Behaviour"""

    config: DataT  # NOTE: check _ExampleConfig in brick.field
