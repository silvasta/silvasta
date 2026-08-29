"""
Good one, maybe new Descriptor: PathGuard.Dir

.
"""

import functools
from collections.abc import Callable
from pathlib import Path
from typing import Any, Self

from ....brick.forge.blueprint import StaticFuncMeta, StaticFuncMetaData
from . import _ensure
from ._input import PathSpec

type Getter = Callable[[Any], Path]
type Logic = Callable[..., Path]


class GuardedAttr:
    """Data descriptor: instance.attr -> Path, assignment forbidden."""

    def __init__(
        self,
        fget: Getter | None,
        *,
        logic: Logic,
        **policy: Any,
    ) -> None:
        self.fget = fget
        self.logic = logic
        self.policy = policy
        self.public_name = ""
        if fget is not None:
            functools.update_wrapper(self, fget)

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name

    def __call__(self, fget: Getter) -> Self:
        if self.fget is not None:
            raise TypeError(f"{type(self).__name__} already bound")
        return GuardedAttr(fget, logic=self.logic, **self.policy)

    def __get__(
        self, obj: object | None, owner: type | None = None
    ) -> Self | Path:
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError(f"{self.public_name} has no getter")
        path = self.fget(obj)
        return self.logic(path, **self.policy)

    def __set__(self, obj: object, value: object) -> None:
        raise AttributeError(f"cannot assign to path {self.public_name!r}")


def Val(logic: Logic, /, **default_policy: Any) -> Callable[..., GuardedAttr]:
    """Build a PathGuard.Dir-style decorator from a Path -> Path logic function."""

    def factory(
        fget: Getter | None = None,
        /,
        **policy: Any,
    ) -> GuardedAttr:
        bound = default_policy | policy
        attr = GuardedAttr(fget, logic=logic, **bound)
        return attr if fget is not None else attr

    return factory


Dir = Val(_ensure._ensure_dir_logic)
File = Val(_ensure._ensure_file_logic, raise_error=True, default_content=None)


class PathGuard(metaclass=StaticFuncMeta, data=StaticFuncMetaData):
    # Dir = _ensure.Dir  # factory -> GuardedAttr instance
    # File = _ensure.File
    # Val = _ensure.Val
    Dir = Dir  # factory -> GuardedAttr instance
    File = File
    Val = Val


MustExist = PathGuard.Val(lambda p: PathSpec.ok(p, must_exists=True))


class Some:
    @MustExist
    def lock_file(self) -> Path:
        return self.config_dir / "lock"


class SstPaths:
    @PathGuard.Dir
    def plot_dir(self) -> Path:
        return self.project_root / self._names.plot_dir

    @PathGuard.File(default_content="", raise_error=True)
    def input_prompt(self) -> Path:
        return Path.cwd() / self._names.prompt

    @PathGuard.unique(ensure_parent=True)
    def summary_file(self, suffix: str = "md") -> Path:
        return self.data_dir / self._names.summary_file(suffix=suffix)

    def dot_env(self) -> Path:
        return PathGuard.file(
            self.dot_env_unconfirmed,
            default_content=self._defaults.dot_env_content,
        )
