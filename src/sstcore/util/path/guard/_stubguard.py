"""
Assemble Stub Path and Module Operations to ModuleGuard

                             DependencyLevel.sstcore.util.path.guard[5]
"""

__all__: list[str] = [
    "ModuleGuard",
]


from ....brick.color.box import Colors
from ....brick.reflect import clsname
from ....forge.engine import StaticFuncMeta, StaticFuncMetaData
from ....port._modulepath import DotPath, ModulePath
from .. import _module
from ._field import LazyModuleField

colors = Colors()


ModuleGuardMetaInput = StaticFuncMetaData(
    name=lambda cls: f" {clsname(cls)} ",
    rich=f"{colors.azure('StubPath')}{colors.teal('Guard')}",
    cli="Resolution, safety, and backups for Python AST Stub generation",
    color=3,
)


class ModuleGuard(metaclass=StaticFuncMeta, data=ModuleGuardMetaInput):
    """Safety and Comfort for Module-to-Filesystem and Stub File Generation"""

    Spec: type[_module.ModuleSpec] = _module.ModuleSpec
    Path: type[ModulePath] = ModulePath
    Dot: type[DotPath] = DotPath

    name = _module.module_name
    public = _module.public_package
    dir = _module.package_dir
    file = _module.module_file
    root = _module.module_root
    submodules = _module.iter_submodules
    importing = _module.importing
    lazy_loader = _module.lazy_loader

    LazyField = LazyModuleField
