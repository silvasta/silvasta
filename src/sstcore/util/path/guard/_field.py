"""
Mound Magic Fields to PathGuard for Hybrid Usage

                         DependencyLevel.sstcore.util.path.guard[2]
"""

# STRATEGY: think about when to use which approach
# - regular decorator
# - field, how to mount?
# - where is the spec defined?

# NEXT: check how to use and prepara a few examples

__all__: list[str] = [
    "PathGuardField",
    "DirField",
    "FileField",
    "UniqueField",
    "PathSpecField",
]

from collections.abc import Callable
from pathlib import Path
from typing import Any, Self, Unpack, overload

from ....brick import reflect
from ....brick.field import DeleteField, FieldDecorator, ReadField, ValidField
from ....port import attach
from ....port.attach import FieldLoader
from ....port.link import portlink
from ....util.path._modulecast import ModuleArg, ModuleSpec
from .._pathcast import PathArg, PathInput, PathSpec, PathStrategy
from . import _ensure, _increment


@portlink(attach.ReadDescriptor)
class PathGuardField(
    DeleteField,
    ReadField[Path],
    FieldDecorator[[Any], PathArg],
):
    """
    Hybrid Descriptor that runs a getter method and applies PathGuard logic.

    - Supports both `@PathGuard.Dir` and `@PathGuard.Dir(lazy=True)`
    - Evaluates to a `Path` on attribute access (`instance.attr`)
    - Read-only on assignment (`instance.attr = x` raises `FieldRaiser.ReadOnly`)
    - Supports cache invalidation via `del instance.attr` when `lazy=True`
    """

    logic: PathStrategy

    def __init__(
        self,
        func: FieldLoader[PathArg] | None = None,
        /,
        *,
        logic: PathStrategy | None = None,
        lazy: bool = False,
        **policy: Any,
    ) -> None:
        if logic is not None:
            self.logic = logic
        self.lazy: bool = lazy
        self.policy: dict[str, Any] = policy
        super().__init__(func)

    def read(self, unit: object) -> Path:
        """Store and Read function value from Unit or Recompute on any Call"""

        if self.lazy and self._has_val(unit):
            return self._get_val(unit)

        if self.target_func is None:
            raise self.raiser.Function(self, unit, "Missing target_func!")

        raw_path: PathArg = self.target_func(unit)
        resolved: Path = type(self).logic(raw_path, **self.policy)

        if self.lazy:
            self._set_val(unit, resolved)

        return resolved

    def remove(self, unit: object) -> None:
        """Clear cached path if lazy=True otherwise raise ReadOnly"""
        if self.lazy:
            super().remove(unit)
        else:
            raise self.raiser.ReadOnly(self, unit, text="LazyMode for Delete!")


class DirField(PathGuardField):
    """Ensure directory exists when attribute is accessed."""

    logic: PathStrategy = _ensure._dir_logic

    def __init__(
        self,
        func: FieldLoader[PathArg] | None = None,
        /,
        *,
        lazy: bool = False,
    ) -> None:
        super().__init__(func, lazy=lazy)


class FileField(PathGuardField):
    """Ensure file exists (or write default_content) when attribute is accessed."""

    logic: PathStrategy = _ensure._file_logic

    def __init__(
        self,
        func: FieldLoader[PathArg] | None = None,
        /,
        *,
        raise_error: bool = True,
        default_content: str | None = None,
        lazy: bool = False,
    ) -> None:
        super().__init__(
            func,
            lazy=lazy,
            raise_error=raise_error,
            default_content=default_content,
        )


class UniqueField(PathGuardField):
    """Provide an auto-incremented unique Path when attribute is accessed."""

    logic: PathStrategy = _increment.unique_candidate

    def __init__(
        self,
        func: FieldLoader[PathArg] | None = None,
        /,
        *,
        ensure_parent: bool = False,
        lazy: bool = False,
    ) -> None:
        super().__init__(
            func,
            lazy=lazy,
            ensure_parent=ensure_parent,
        )


@portlink(attach.ValidDescriptor)
class PathSpecField(ReadField[Path], ValidField[PathArg]):
    """
    Assignable descriptor that normalizes and validates `PathArg` via `PathSpec`.

    Example:
        class Config:
            source = PathGuard.SpecField(must_exists=True, resolve=True)
            output = PathGuard.SpecField(ensure_parent=True)
    """

    def __init__(
        self,
        *,
        default: PathArg | Any = ...,
        frozen: bool = False,
        **spec_kwargs: Unpack[PathInput],
    ) -> None:
        self.spec_kwargs: PathInput = spec_kwargs
        init_kwargs: dict[str, Any] = {"frozen": frozen}
        if default is not ...:
            init_kwargs["default"] = default
        super().__init__(**init_kwargs)

    def validate(self, unit: object, value: PathArg) -> Path:
        _ = unit
        return PathSpec.ok(value, **self.spec_kwargs)

    def read(self, unit: object) -> Path:
        if not self._has_val(unit) and self.default is not ...:
            validated: Path = self.validate(unit, self.default)
            self._set_val(unit, validated)
            return validated
        return super().read(unit)


class LazyModuleField[T]:  # CHECK: how well does this work?
    """Resolve and Cache 'pkg.mod:Attr' ModulePath on first access"""

    def __init__(
        self,
        fget: Callable[[Any], ModuleArg],
        *,
        call_if_callable: bool = False,
    ) -> None:
        self.fget: Callable[[Any], ModuleArg] = fget
        self.call_if_callable: bool = call_if_callable
        self.attr_name: str = reflect.funcname(fget)

    @overload
    def __get__(self, unit: None, owner: type | None) -> Self: ...
    @overload
    def __get__(self, unit: object, owner: type | None) -> T: ...
    def __get__(self, unit: Any, owner: type | None = None) -> T | Self:
        _ = owner
        if unit is None:
            return self
        _mp = ModuleSpec.ok(self.fget(unit), resolve=True, must_exists=True)
        val: T = _mp.lazy_loader(call_if_callable=self.call_if_callable)()
        setattr(unit, self.attr_name, val)  # Cache on instance dict
        return val
