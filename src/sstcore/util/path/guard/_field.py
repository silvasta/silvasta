"""
Good one, maybe new Descriptor: PathGuard.Dir

.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from ....brick.field import Derived
from . import _ensure

type Getter = Callable[[Any], Path]
type Logic = Callable[..., Path]


class PathGuardField(Derived[Path]):
    """
    Descriptor that runs a getter then applies PathGuard logic.

    - Read-only by design (assignment raises).
    - Supports __set_name__ for clean error messages.
    - Can be used directly or via the Val/Dir/File factories.
    """

    def __init__(
        self, *args: Any, derived: Getter, logic: Logic, **policy: Any
    ) -> None:
        self.logic: Logic = logic
        self.policy: dict[str, Any] = policy
        super().__init__(*args, derived=derived)

    def read(self, unit: object) -> Path:
        base_path: Path = super().read(unit)
        return self.logic(base_path, **self.policy)

    def __set__(self, unit: object, value: object) -> None:
        # EXTRACT: and create: NoWriteField
        _cls_attr = self._cls_attr_name(unit)
        raise AttributeError(f"{_cls_attr} Path is not Writable!")


def Val(logic: Logic, /, **default_policy: Any):  # noqa: N802
    """
    Create a descriptor factory for a guard logic.

    Usage:
        @PathGuard.Dir
        def logs(self): ...

        @PathGuard.File(raise_error=False, default_content="")
        def config(self): ...
    """

    def factory(fget: Getter | None = None, /, **policy: Any):
        bound: dict[str, Any] = default_policy | policy
        if fget is None:

            def wrapper(fn: Getter) -> PathGuardField:
                return PathGuardField(fn, logic, **bound)

            return wrapper
        return PathGuardField(fget, logic, **bound)

    return factory


Dir = Val(_ensure._ensure_dir_logic)
File = Val(_ensure._ensure_file_logic, raise_error=True, default_content=None)
Unique = Val(_ensure._get_unique_candidate, ensure_parent=False)
