"""
Find and Match Package- and Module- with FileSystem Paths

                           DependencyLevel.sstcore.util.path[4.X.0]
"""

__all__: list[str] = [
    "ModuleSpec",
    "ModuleCaster",
    "ModuleArg",
    "ModuleInput",
    "ModuleCastInput",
    #
    "TargetModule",
    "ValidModule",
    "SourceModule",
]

from typing import Annotated, Self
from typing import Unpack as _U  # noqa:N814

from typing_extensions import TypedDict

from ...brick.call import ArgCast, ArgCaster, ArgCasting, CastInput
from ...port._modulepath import ModulePath
from ...port.empty import VOID, MayBe
from ...port.link import portlink
from ...port.structures import ArgSpec


class _ModuleInput(TypedDict, total=False):
    require_attr: bool
    allow_relative: bool
    resolve: bool
    module_exists: bool
    must_exists: bool


class ModuleCastInput(
    _ModuleInput, CastInput[ModulePath], total=False, closed=True
):
    """Extend ModuleInput with Default Casting Input."""


class ModuleInput(_ModuleInput, total=False, closed=True): ...


class ModuleSpec(ArgSpec[ModulePath], frozen=True):
    """Normalize and validate input into a canonical ModulePath"""

    require_attr: bool = False
    allow_relative: bool = False
    resolve: bool = False
    module_exists: bool = False
    must_exists: bool = False

    @classmethod
    def from_path(
        cls, target: MayBe[ModuleArg] = VOID, /, **tkw: _U[ModuleInput]
    ) -> Self:
        if isinstance(target, (str, ModulePath)):
            return cls.normalize(target, **tkw)
        raise TypeError(
            f"Expected str or ModulePath, got {type(target).__name__}"
        )

    @classmethod
    def normalize[ScanT](
        cls, target: MayBe[ModuleArg | ScanT] = VOID, /, **tkw: _U[ModuleInput]
    ) -> Self:
        if target is VOID:
            raise ValueError("ModuleSpec Requires non-empty Target")

        _kw = tkw.get
        resolve: bool = _kw("resolve", False)
        relative: bool = _kw("allow_relative", resolve)

        match target:
            case cls():
                _spec: Self = target.evolve(**tkw)
                modulepath: ModulePath = _spec.target

            case ModulePath():
                modulepath: ModulePath = target

            case str():
                modulepath = ModulePath.parse(target, allow_relative=relative)

            case _:
                modulepath: ModulePath = ModulePath.identify(target)

        if resolve and modulepath.is_relative:
            _check = _kw("module_exists", False) or _kw("must_exists", False)
            modulepath = modulepath.resolve(check_exists=_check)

        return cls(target=modulepath, **tkw)

    def validate(self) -> ModulePath:
        """Execute syntactic and existence checks on the normalized ModulePath."""
        mp: ModulePath = self.target

        if not self.allow_relative and not self.resolve and mp.is_relative:
            raise ValueError(f"Relative module path not allowed: {mp}")

        if self.require_attr and not len(mp.quals):
            raise ValueError(
                f"Expected 'package.module:Attr' with explicit ':Attr', got {mp}"
            )

        if len(mp.quals) and "<locals>" in mp.qualname:
            raise ValueError(f"Local object {mp} is not globally importable")

        if self.module_exists and not mp.module_exists():
            raise ModuleNotFoundError(f"Module does not exist: {mp.module}")

        if self.must_exists and not mp.importable():
            raise ImportError(f"Module target cannot be imported: {mp}")

        return mp


ModuleArg = ModuleSpec | ModulePath | str


class _ModuleBackup(TypedDict):
    backup: bool


class _ModuleDir(TypedDict):
    subfolder: str


class _ModulePackage(TypedDict):
    package: str | None


class ModulInitInput(_ModuleBackup, _ModulePackage, closed=True):
    """Create Path for __init__.pyi"""


class ModulDirInput(_ModuleDir, _ModulePackage):
    """Accept Kwargs to make it easy for the others to forward here"""


class ModulFullInput(_ModuleDir, _ModuleBackup, _ModulePackage, closed=True):
    """Single Stub file optional with subdir and prefix"""


@portlink(ArgCasting)
class ModuleCaster(ArgCaster[ModuleArg, ModulePath]):
    _input_types = (ModuleSpec, ModulePath, str)

    def __init__(self, **tkw: _U[ModuleCastInput]):
        super().__init__(**tkw)

    def cast[T](self, target: MayBe[ModuleArg | T], /) -> ModulePath:
        return ModuleSpec.ok(target, **self.kwargs)


ArgCast.register(ModulePath, ModuleCaster())
ArgCast.register(ModuleArg, ModuleCaster())

type TargetModule = Annotated[
    ModuleArg,
    ModuleCaster(),
]
type ValidModule = Annotated[
    ModuleArg,
    ModuleCaster(module_exists=True),
]
type SourceModule = Annotated[
    ModuleArg,
    ModuleCaster(
        require_attr=True,
        must_exists=True,
    ),
]
