"""
Define the Shape of the Field Descriptors

- Attach attributes to Classes
                                    DependencyLevel.sstcore.port[3]
"""

__all__: list[str] = [
    "Descriptor",
    "ReadDescriptor",
    "WriteDescriptor",
    "DeleteDescriptor",
    "Descriptor",
    #
    "ValidDescriptor",
    "TypedDescriptor",
    "LazyDescriptor",
    "FieldLoader",
    "CallingDescriptor",
    "Calling",
    #
    "EventDescriptor",
    "ConfigDescriptor",
]


import typing as _t
from collections.abc import Callable as _Callable
from enum import Enum as _Enum

from .event.emit import Emit as _Emit
from .solid import PolicyEnum as _PolicyEnum


class Descriptor[T](_t.Protocol):
    """Define the Base Contract for any Field"""

    def __set_name__(self, owner: type, name: str) -> None: ...

    public_name: str
    private_name: str


#  LINE: -- Level 1 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ReadDescriptor[T](Descriptor, _t.Protocol):
    """Define the Base Getter Non-Data Descriptor"""

    @_t.overload
    def __get__(self, unit: None, owner: type) -> _t.Self: ...
    @_t.overload
    def __get__(self, unit: _t.Any, owner: type) -> T: ...
    def __get__(
        self, unit: _t.Any | None, owner: type | None
    ) -> T | _t.Self: ...
    def read(self, unit: object) -> T: ...


class WriteDescriptor[T](Descriptor, _t.Protocol):
    """Define the Base Setter Data Descriptor"""

    def __set__(self, unit: _t.Any, value: T) -> None: ...
    def write(self, unit: object, value: T) -> None: ...


class DeleteDescriptor(Descriptor, _t.Protocol):
    """Define the Base Eraser Data Descriptor"""

    def __delete__(self, unit: _t.Any) -> None: ...
    def remove(self, unit: object) -> None: ...


class DecoDescriptor[**In, Out](Descriptor, _t.Protocol):
    """Define the Descriptor that Decorates"""

    def __init__(
        self,
        func: _Callable[In, Out] | None = None,
        *args: _t.Any,
        **kwargs: _t.Any,
    ):
        """Insert Initial Strategy or Bind Decorator"""

    def __call__(self, func: _Callable[In, Out]) -> _t.Self:
        """Decorate Initial Strategy for Bound Decorator"""


#  LINE: -- Extensions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ValidDescriptor[T](WriteDescriptor[T], _t.Protocol):
    def validate(self, unit: object, value: T) -> T:
        """Confirm the Value while attaching"""


class TypedDescriptor[T](ValidDescriptor[T], _t.Protocol):
    def __init__(self, types: type[T] | tuple[type, ...]) -> T:
        """Confirm the Type while attaching"""


class LazyDescriptor[T](Descriptor[T], _t.Protocol):
    def __init__(self, loader: FieldLoader) -> None:
        """Prepare Attribute for load on first call"""

    loader: FieldLoader


class FieldLoader[T](_Callable, _t.Protocol):
    def __call__(self, _: _t.Any, /) -> T:
        """Execute with exactly the attached Instance as Input"""


class PolicyDescriptor[EnumT: _PolicyEnum](
    TypedDescriptor, ReadDescriptor, _t.Protocol
):
    """Govern the Enum including match and dispatch"""


class MatchingDescriptor[EnumT: _PolicyEnum](PolicyDescriptor, _t.Protocol):
    """Govern the Enum including match and dispatch"""

    def match(self, state: EnumT, unit: object):  # LATER: specify
        """Launch match_func, get override or Raise"""


#  LINE: -- Strategy -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CallingDescriptor[**In, Out](
    DecoDescriptor,
    ValidDescriptor[_Callable[In, Out]],
    ReadDescriptor[_Callable[In, Out]],
    DeleteDescriptor,
    _t.Protocol,
):
    """Switch Callable Attribute (Method) with enforced Rules"""

    def switch(self, func: _Callable[In, Out]) -> _t.Self:
        """Install new LSP conform Method"""


class MorphingDescriptor(CallingDescriptor, _t.Protocol):
    """Switch Callable Attribute (Method) with less Rules"""

    def morph(self, func: _Callable) -> _t.Self:
        """Install new Method with possible LSP Violation"""


@_t.runtime_checkable
class Calling[**In, Out](_t.Protocol):
    # LATER: check name, although attach.Calling (when used like this) quite good
    """Define a Callable marked as Field"""

    __field_kind__: type[CallingDescriptor[In, Out]]

    def __call__(self, *args: In.args, **kwargs: In.kwargs) -> Out: ...


#  LINE: -- Next Steps -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Transition[T](_t.Protocol):  # LATER: move to state transition
    def __call__(self, unit: object, current: T, next: T, **kwargs) -> _t.Any:
        """Calculate Actions depending on the State Pair"""


class TransitionDescriptor[T: _Enum](TypedDescriptor[T], _t.Protocol):
    def __init__(self, *args, transition: Transition, **kwargs) -> None: ...
    def state_graph_evaluation(
        self, unit: object, current: T, next: T
    ) -> _t.Any:
        """Implement rigid state-machine rules here"""


class StateDescriptor[T: _Enum](TransitionDescriptor[T]):
    """Govern the Lifecycle of the State"""


class EventDescriptor[T](_t.Protocol):
    emit: _Emit

    def __init__(self, func: _Emit) -> None:
        """Listen to all Channels and Message to EventBus"""


class ConfigDescriptor[DataT](_t.Protocol):
    def update(self, **config: DataT) -> _t.Any:
        """Modify Configuration and change Behaviour"""

    config: DataT  # NOTE: check _ExampleConfig in brick.field
