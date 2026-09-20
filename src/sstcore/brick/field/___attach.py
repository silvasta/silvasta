"""
EXPERIMENTAL

- Provide Constructor for class body or decorated Fields

                                               DependencyLevel[max]
"""

# TASK: find best location:
# - sstcore.forge looks somehow like the destinated location

from typing import Any, Protocol

from ...port import attach
from ...port.govern import Option
from ._base import NamedField
from ._combine import DerivedField, Forward, LazyField, RequiredField
from ._decorate import DecoratedField
from ._strategy import DynamicStrategy, StrategyField

#  LINE: -- Definitions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FieldOption(Option):
    LAZY: type[NamedField] = LazyField
    REQUIRED: type[NamedField] = RequiredField
    DERIVED: type[NamedField] = DerivedField
    FORWARD: type[NamedField] = Forward


class DecoFieldOption(Option):
    # IDEA: PathGuardField
    # Issue: lives in sstcore.util.path.guard...
    # -> assemble this at a very late point! directly before export
    # -> assemble this in sstcore.forge, move util.path.guard._filed there
    STRATEGY: type[DecoratedField] = StrategyField
    MORPH: type[DecoratedField] = DynamicStrategy


#  LINE: -- Ideas for Constructor Functions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def mount1(*args, **kwargs) -> attach.Descriptor:
    """Descriptor produced by Annotation and Input"""
    raise NotImplementedError(args, kwargs)


def mount2[T](*args, **kwargs) -> attach.Descriptor[T]:
    """Descriptor produced by Annotation and Input"""
    raise NotImplementedError(args, kwargs)


def mount3[T: Any](*args, default: T, **kwargs) -> attach.ReadDescriptor[T]:
    """Descriptor produced by Annotation and Input"""
    raise NotImplementedError(args, default, kwargs)


def mount4(*args, **kwargs) -> Any:
    """Descriptor produced by Annotation and Input"""
    raise NotImplementedError(args, kwargs)


def mounted(*args, **kwargs) -> attach.DecoDescriptor:
    """DecoDescriptor produced by decorated Method and Input"""
    raise NotImplementedError(args, kwargs)


#  LINE: -- Ideas for Constructor Protocols -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class MountField(Protocol):
    def __call__(self) -> attach.Descriptor: ...


class _MountField(Protocol):
    def mount(self) -> attach.Descriptor: ...


class DecorateField(Protocol):
    def __call__(self) -> attach.DecoDescriptor: ...


class _DecorateField(Protocol):
    def mounted(self) -> attach.Descriptor: ...


#  LINE: -- Ideas for Usage -- -- - -- -- - -- -- - -- -- - -- -- - -- --

_args = ()
_kwargs = {}


class _ExampleClass1:
    test1: attach.Descriptor = mount1(*_args, **_kwargs)
    test21: attach.Descriptor[int] = mount2(*_args, **_kwargs)
    test22: attach.Descriptor = mount2(*_args, **_kwargs)
    test3: int = mount3(*_args, default=0, **_kwargs)  # ty:ignore
    test3: int = mount4(*_args, **_kwargs)

    @mounted
    def test_fn2(self, *args, **kwargs) -> Any: ...

    @mounted()
    def test_fn3(self, *args, **kwargs) -> Any: ...

    @mounted(*_args, **_kwargs)
    def test_fn4(self, *args, **kwargs) -> Any: ...


class _FieldOption1(Option):
    """Default on Index 0"""  # TODO: ensure in BaseEnum/EnumZero

    LAZY: type[NamedField] = LazyField
    REQUIRED: type[NamedField] = RequiredField
    DERIVED: type[NamedField] = DerivedField
    FORWARD: type[NamedField] = Forward

    def __call__(self, *args, **kwargs) -> NamedField:
        raise NotImplementedError(args, kwargs)


mount = _FieldOption1


class _ExampleClass2:
    test1: NamedField = mount.LAZY(*_args, **_kwargs)
    test2: NamedField = mount.REQUIRED(*_args, **_kwargs)

    # FIX: modify base Option for access on Enum.__call__
    test3: LazyField = mount(*_args, **_kwargs)  # ty:ignore
