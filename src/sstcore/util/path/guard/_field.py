"""
Mound Magic Fields to PathGuard for Hybrid Usage

                         DependencyLevel.sstcore.util.path.guard[2]
"""

__all__: list[str] = [
    "PathGuardField",
    "DirField",
    "FileField",
    "UniqueField",
    "PathSpecField",
    # TODO: give alias in _assemble, why here??
    "Dir",
    "File",
    "Unique",
    "SpecField",
]

from collections.abc import Callable
from pathlib import Path
from typing import Any, Unpack

from ....brick.field import DeleteField, FieldDecorator, ReadField, ValidField
from ....port import attach
from ....port.attach import FieldLoader
from ....port.link import portlink
from . import _ensure
from ._arg import PathArg, PathInput, PathSpec

type PathStrategy = Callable[..., Path]


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

    logic: PathStrategy = _ensure._unique_candidate

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


# Aliases for PathGuard class assembly
Dir = DirField
File = FileField
Unique = UniqueField
SpecField = PathSpecField
