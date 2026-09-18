"""
Good one, maybe new Descriptor: PathGuard.Dir

.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from ....brick.field import DecoratedField, DerivedField, OnlyReadField
from ....port.attach import FieldLoader
from . import _ensure

type PathStrategy = Callable[..., Path]


# NEXT: check if this new version is better, delete rest
class DirField(DecoratedField[Path], OnlyReadField):
    # TODO: check: class DirGuardField(DerivedField[Path]):
    """Specialized decorator that locks in the PathGuard logic."""

    def __init__(
        self,
        target: FieldLoader[Path] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Pre-bake the directory logic into the args/kwargs
        self.logic: PathStrategy = _ensure._ensure_dir_logic
        # IDEA: move logic to subhook with optional override?
        # - maybe better than this entire additional __init__
        super().__init__(target, *args, **kwargs)

    def read(self, unit: object) -> Path:
        base_path = super().read(unit)
        return self.logic(base_path)


# AI: this was the former version
class PathGuardField(DerivedField[Path]):
    """
    Descriptor that runs a getter then applies PathGuard logic.

    - Read-only by design (assignment raises).
    - Supports __set_name__ for clean error messages.
    - Can be used directly or via the Val/Dir/File factories.
    """

    def __init__(
        self,
        *args: Any,
        derived: FieldLoader[Path],
        logic: PathStrategy,
        **policy: Any,
    ) -> None:
        self.logic: PathStrategy = logic
        self.policy: dict[str, Any] = policy
        super().__init__(*args, derived=derived)

    def read(self, unit: object) -> Path:
        base_path: Path = super().read(unit)
        return self.logic(base_path, **self.policy)

    def __set__(self, unit: object, value: object) -> None:
        # EXTRACT: create: NoWriteField?
        _cls_attr = self.name(unit)
        raise AttributeError(f"{_cls_attr} Path is not Writable!")


# AI: this was like the template for the decorator
def Val(logic: PathStrategy, /, **default_policy: Any):  # noqa: N802
    # TASK: this as factory mixin in brick.field?
    """
    Create a descriptor factory for a guard logic.

    Usage:
        @PathGuard.Dir
        def logs(self): ...

        @PathGuard.File(raise_error=False, default_content="")
        def config(self): ...
    """

    def factory(fget: FieldLoader | None = None, /, **policy: Any):
        bound: dict[str, Any] = default_policy | policy
        if fget is None:

            def wrapper(fn: FieldLoader) -> PathGuardField:
                return PathGuardField(fn, logic, **bound)

            return wrapper
        return PathGuardField(fget, logic, **bound)

    return factory


# MOVE: ._assemble?
Dir = Val(_ensure._ensure_dir_logic)
File = Val(_ensure._ensure_file_logic, raise_error=True, default_content=None)
Unique = Val(_ensure._get_unique_candidate, ensure_parent=False)
