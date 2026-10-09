import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

from sstcore.util.path.guard import PathInput, PathSpec


@dataclass(frozen=True, slots=True)
class ArgMeta:
    """Metadata ArgCast understands. Anything else is ignored."""


@dataclass(frozen=True, slots=True)
class ArgContext[M: ArgMeta]:
    name: str
    param: inspect.Parameter
    annotation: Any
    meta: tuple[M, ...] = ()

    @property
    def has_default(self) -> bool:
        return self.param.default is not inspect.Parameter.empty

    def find(self, kind: type[M]) -> M | None:
        return next((m for m in self.meta if type(m) is kind), None)


@dataclass(frozen=True, slots=True)
class PathContextRules(ArgMeta):
    resolve: bool = False
    must_exists: bool = False


def coerce_path(raw: Any, ctx: ArgContext) -> Path:
    rules = ctx.find(PathContextRules) or PathContextRules()
    return PathSpec.ok(
        raw, resolve=rules.resolve, must_exists=rules.must_exists
    )


type SourcePath = Annotated[
    PathInput, PathContextRules(must_exists=True, resolve=True)
]
type TargetPath = Annotated[PathInput, PathContextRules()]


def print_path(path: SourcePath):
    print(path.name)
