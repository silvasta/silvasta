"""
Assemble Stub Path and Module Operations to StubFileGuard

                             DependencyLevel.sstcore.util.path.guard[5]
"""

__all__: list[str] = [
    # IDEAS:
    "StubFileGuard",
    # "StubGuard",
    # "StubPathGuard",
]

from collections.abc import Callable
from pathlib import Path
from typing import Any

from ....brick.color.box import Colors
from ....brick.labor import clsname
from ....forge.engine.blueprint import StaticFuncMeta, StaticFuncMetaData
from ....port.color import ColorBox
from ....port.files import SyncMode
from .. import _module
from . import _ensure, _operate

colors: ColorBox = Colors()  # type: ignore


def stub_file_init(
    obj: Any, *, package: str | None = None, backup: bool = True
) -> Path:
    """Create Package Init StubFile Path and ensure Backup and Writable"""

    # PARAM: change init_stub defaults here
    stub_dir: Path = _module.stub_root(obj, package)
    init_stub: Path = stub_dir / "__init__.pyi"

    _ensure.dir(init_stub.parent)

    return (
        _ensure_backup(init_stub)
        if backup and init_stub.exists()
        else init_stub
    )


def _ensure_backup(target: Path) -> Path:
    # MOVE: integrate into guard._ensure
    # LATER: new branch in _ensure pipeline
    """NEW: Backup Function for PathGuard"""
    if target.exists():
        _operate.copy(
            source=target,
            target=target.with_suffix(".pyi.bak"),
            mode=SyncMode.INCREMENT,
        )
    return target


def single_stub_file(  # IDEAS: make_stub_file,get_stub_file, else?
    obj: Any, *, prefix: str, package: str | None = None, backup: bool = True
) -> Path:
    """Create Single StubFile Path and ensure Backup and Writable"""

    # PARAM: change stub_file defaults here
    stub_dir: Path = _module.stub_root(obj, package)
    stub_file: Path = stub_dir / "_stubs" / f"_{prefix.lower()}.pyi"

    _ensure.dir(stub_file.parent)

    return (
        _ensure_backup(stub_file)
        if backup and stub_file.exists()
        else stub_file
    )


StubGuardMetaInput = StaticFuncMetaData(
    name=lambda cls: f" {clsname(cls)} ",
    rich=f"{colors.azure('StubPath')}{colors.teal('Guard')}",
    cli="Resolution, safety, and backups for Python AST Stub generation",
    color=3,
)


class StubFileGuard(metaclass=StaticFuncMeta, data=StubGuardMetaInput):
    """Safety and Comfort for generating Python Stub Files"""

    # AI: the below docstring (imitations) and type hints are DX essential
    # - the .pyi defines the public interface, this is for internal use

    """Category 1: Base Introspection (Clean namespace mapping)"""
    module_name: Callable = _module.module_name
    public_package: Callable = _module.public_package

    #
    """Category 2: Directory Guard (get_stub_dir already has @PathGuard.Dir!)"""
    get_stub_dir: Callable = _module.get_stub_dir
    stub_root: Callable = _module.stub_root

    #
    """Category 3: The 1-Line Verification Feature"""
    stub_file_init: Callable = stub_file_init
    single_stub_file: Callable = single_stub_file
