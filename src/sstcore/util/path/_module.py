"""
Find and Match Package- and Module- with FileSystem Paths

- ModuleName: "sstcore.brick.stack" -> is Dotted

                               DependencyLevel.sstcore.util.path[1]
"""

# TASK: Separate Module and Stub topics
# - anything already handled by ModulePath: delete
# - anything for Stub, probably move -> .guard._stub_guard (or config)
# - if something remaining, either:
#   - mount to ModulePath (make original private, mount to derivative, expose derivative)
#   - expose directly here

__all__: list[str] = [
    "module_name",
    "public_package",
    "package_dir",
    "stub_root",
    "get_stub_dir",
    #
    "ModuleSpec",
    "ModuleArg",
    "ModuleInput",
    "AnyModulePath",
    "ModuleCaster",
]

import importlib.util
import inspect
from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Annotated, Any, Self, TypedDict, Unpack

from ...brick.call import ArgCast, ArgCaster
from ...port.empty import VOID, MayBe
from ...port.structures import ArgSpec
from ...port.structures._module import ModulePath


def module_name(obj: Any) -> str:
    """Accepts modules, classes, functions, and callables"""

    if inspect.ismodule(obj):
        return obj.__name__

    if inspect.isclass(obj) or inspect.isfunction(obj):
        return obj.__module__

    call: Any | None = getattr(obj, "call", None)

    if isinstance(call, Callable) and getattr(call, "__module__", None):
        return call.__module__

    return type(obj).__module__


def public_package(module_name: str) -> str:
    """Walk upwards until next public Package"""

    parts: list[str] = module_name.split(".")

    while len(parts) > 1 and parts[-1].startswith("_"):
        parts.pop()

    return ".".join(parts)


def package_dir(dot_path: str) -> Path:
    """Resolve DotPath ModuleName to FileSystem Location or Raise"""

    if (spec := importlib.util.find_spec(dot_path)) is None:
        raise ModuleNotFoundError(f"Missind Module: {dot_path=}")

    if spec.submodule_search_locations:
        return Path(next(iter(spec.submodule_search_locations))).resolve()

    if not spec.origin or spec.origin in {"built-in", "frozen"}:
        raise ValueError(f"Not found on Disk: {dot_path!r}!")

    return Path(spec.origin).resolve().parent


def stub_root(obj: Any, package: str | None = None) -> Path:
    module: str = module_name(obj)
    dot_path: str = package or public_package(module_name=module)
    root: Path = package_dir(dot_path)
    return root


def get_stub_dir(
    target: str | ModuleType | Path, subdir: str = "_stubs"
) -> Path:  # LATER: target: DotPathSpec ?
    """Stable resolution of where stubs should live."""

    match target:
        case Path():
            base_dir: Path = target if target.is_dir() else target.parent
        case str():
            base_dir: Path = package_dir(target)
        case _:
            base_dir: Path = package_dir(module_name(target))

    path: Path = base_dir / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path


#  LINE: -- ModuleSpec -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ModuleInput(TypedDict, total=False):
    require_attr: bool
    allow_relative: bool
    resolve: bool
    module_exists: bool
    must_exists: bool


ModuleArg = ModulePath | str

type AnyModulePath = Annotated[
    ModulePath,
    ModuleCaster(),  # CHECK: any defaults?
]


class ModuleSpec(ArgSpec[ModulePath], frozen=True):
    """Normalize and validate input into a canonical ModulePath"""

    require_attr: bool = False
    allow_relative: bool = False
    resolve: bool = False
    module_exists: bool = False
    must_exists: bool = False

    @classmethod
    def from_path(
        cls, target: MayBe[ModuleArg] = VOID, /, **kwargs: Unpack[ModuleInput]
    ) -> Self:
        if isinstance(target, (str, ModulePath)):
            return cls.normalize(target, **kwargs)
        raise TypeError(
            f"Expected str or ModulePath, got {type(target).__name__}"
        )

    @classmethod
    def normalize(
        cls,
        target: MayBe[ModuleArg | Any] = VOID,
        /,
        **kwargs: Unpack[ModuleInput],
    ) -> Self:
        if target is VOID:
            raise ValueError("ModuleSpec requires a non-empty target")

        resolve: bool = kwargs.get("resolve", False)
        relative: bool = kwargs.get("allow_relative", False) or resolve

        match target:
            case cls():
                _spec: Self = target.evolve(**kwargs)
                _mp: ModulePath = _spec.target
            case ModulePath():
                _mp: ModulePath = target
            case str():
                _mp = ModulePath.parse(target, allow_relative=relative)
            case _:
                _mp: ModulePath = ModulePath.identify(target)

        if resolve and _mp.is_relative:
            _mp = _mp.resolve(
                # CHECK: anchors?
                check_exists=kwargs.get("module_exists", False)
                or kwargs.get("must_exists", False),
            )

        return cls(target=_mp, **kwargs)

    def validate(self) -> ModulePath:
        """Execute syntactic and existence checks on the normalized ModulePath."""
        mp: ModulePath = self.target

        if not self.allow_relative and not self.resolve and mp.is_relative:
            raise ValueError(f"Relative module path not allowed: {mp}")

        if self.require_attr and not mp.has_attr:
            raise ValueError(
                f"Expected 'package.module:ATTR' with explicit ':ATTR', got {mp}"
            )

        if mp.has_attr and "<locals>" in mp.qualname:
            raise ValueError(f"Local object {mp} is not globally importable")

        if self.module_exists and not mp.module_exists():
            raise ModuleNotFoundError(f"Module does not exist: {mp.module}")

        if self.must_exists and not mp.importable():
            raise ImportError(f"Module target cannot be imported: {mp}")

        return mp


class ModuleCaster(ArgCaster[ModuleArg, ModulePath]):
    _input_types = (str, ModuleSpec)  # WARN: is this proper? especially str??

    def __init__(self, **kwargs: Unpack[ModuleInput]) -> None:
        super().__init__(**kwargs)

    def cast(self, target: MayBe[ModuleArg], /) -> ModulePath:
        return ModuleSpec.ok(target, **self.kwargs)


# CHECK: valid registration?? what else?
ArgCast.register(ModuleArg, ModuleCaster())
