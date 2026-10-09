# sstcore/forge/cast/_rules.py
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sstcore.util.path.guard._input import PathSpec


@dataclass(frozen=True, slots=True)
class Resolver:  # REMOVE: ??
    """Generic caster for simple type transformations (e.g., Color, SyncMode)."""

    convert: Callable[[Any], Any]
    use_default_on_error: bool = False  # REMOVE: includ this in handler! apply default always when provided

    def __call__(
        self, raw: Any, /, *, default: Any = inspect.Parameter.empty
    ) -> Any:
        try:
            return self.convert(raw)
        except (ValueError, TypeError, KeyError) as error:
            if (
                self.use_default_on_error
                and default is not inspect.Parameter.empty
            ):
                return default
            raise ValueError(f"Failed to cast {raw!r}") from error


@dataclass(frozen=True, slots=True)
class PathRules:
    resolve: bool = False
    must_exists: bool = False
    ensure_parent: bool = False

    def __call__(
        self, value: Any, default: Any = inspect.Parameter.empty
    ) -> Path:
        if value is inspect.Parameter.empty:
            if default is not inspect.Parameter.empty:
                value = default

        # No re-raise, PathGuardError is already describing enough, and fires according to Spec
        return PathSpec.ok(
            target=value,
            resolve=self.resolve,
            must_exists=self.must_exists,
        )
