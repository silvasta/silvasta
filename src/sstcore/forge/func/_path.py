import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

from ...util.path.guard import PathInput, PathSpec


@dataclass(frozen=True, slots=True)
class PathPolicy:
    resolve: bool = False
    must_exists: bool = False
    ensure_parent: bool = False

    def __call__(
        self,
        raw: Any,
        /,
        *,
        default: Any = inspect.Parameter.empty,
        name: str = "",
        param: inspect.Parameter | None = None,
    ) -> Path:
        path = PathSpec.ok(
            target=raw,
            resolve=self.resolve,
            must_exists=self.must_exists,
        )
        if self.ensure_parent:
            path.parent.mkdir(parents=True, exist_ok=True)
        return path


Source = Annotated[PathInput, PathPolicy(must_exists=True, resolve=True)]
Target = Annotated[PathInput, PathPolicy()]
