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


class GuardedPath(Derived[Path]):
    """Derived Path run through PathGuard logic; assignment is forbidden."""

    def __inij__(
        self, *args: Any, derived: Getter, logic: Logic, **policy: Any
    ) -> None:
        self.logic: Logic = logic
        self.policy: dict[str, Any] = policy
        super().__init__(*args, derived=derived)

    def read(self, unit: object) -> Path:
        base_path: Path = super().read(unit)
        return self.logic(base_path, **self.policy)

    def __set__(self, unit: object, value: object) -> None:
        _cls_attr = self._cls_attr_name(unit)
        raise AttributeError(f"{_cls_attr} Path is not Writable!")


def Val(logic: Logic, /, **default_policy: Any):
    """Build Descriptor Factory for PathGuard methods (@PathGuard.Dir, etc.)."""

    def factory(fget: Getter | None = None, /, **policy: Any):
        bound_policy = {**default_policy, **policy}
        if fget is None:
            return lambda fn: GuardedPath(
                derived=fn, logic=logic, **bound_policy
            )
        return GuardedPath(derived=fget, logic=logic, **bound_policy)

    return factory


Dir = Val(_ensure._ensure_dir_logic)
File = Val(_ensure._ensure_file_logic, raise_error=True, default_content=None)
Unique = Val(_ensure._get_unique_candidate, ensure_parent=False)
