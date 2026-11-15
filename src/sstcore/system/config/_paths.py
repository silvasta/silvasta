"""
Compose and Ensure Paths independent of system or location

- Assemble from Defaults, Names, HomeSetup and any desired input
- Use PathGuard to ensure existence, uniqueness or writability
                                                       DependencyLevel[1]
"""

from typing import Any

__all__: list[str] = [
    "SstPaths",
]

from pathlib import Path
from typing import Unpack as _U  # noqa:N814

from ...port.config import Defaults, Homes, Names, Paths
from ...port.link import portlink
from ...util.path._modulecast import (
    ModulDirInput,
    ModulFullInput,
    ModulInitInput,
)
from ...util.path.guard import ModuleGuard, PathGuard
from ._defaults import SstDefaults
from ._homes import HomeSetup, SstHomes
from ._names import SstNames

ModuleGuard.Path.parse("my.path:Attr")


@portlink(Paths)
class SstPaths:
    def __init__(
        self,
        defaults: Defaults | None = None,
        names: Names | None = None,
        homes: Homes | None = None,
    ):  # LATER: Fields!!
        self._defaults: Defaults = defaults or SstDefaults()
        self._names: Names = names or SstNames()
        self.homes: Homes = homes or SstHomes.from_setup(HomeSetup.GLOBAL)

    @PathGuard.Dir
    def project_root(self) -> Path:
        return self.homes.root

    @PathGuard.Dir
    def config_dir(self) -> Path:
        return self.homes.config

    @PathGuard.Dir
    def log_dir(self) -> Path:
        return self.homes.log

    @PathGuard.Dir
    def data_dir(self) -> Path:
        return self.homes.data

    @PathGuard.Dir
    def plot_dir(self) -> Path:
        return self.project_root / self._names.plot_dir

    @PathGuard.Dir
    def state_dir(self) -> Path:
        return self.homes.state

    def dot_env(self) -> Path:
        return PathGuard.file(
            target=self.dot_env_unconfirmed,
            default_content=self._defaults.dot_env_content,
        )

    @property
    def dot_env_unconfirmed(self) -> Path:
        return self.config_dir / ".env"

    @PathGuard.unique(ensure_parent=True)
    def summary_file(self, suffix: str = "md") -> Path:
        filename: str = self._names.summary_file(suffix=suffix)
        return self.data_dir / filename

    def scanner_cache(self, root: Path | None = None, suffix=".db") -> Path:
        """Work around DiskCache Folder requirement..."""
        dir: Path = root or self.state_dir
        return dir / f"{self._names.scanner_cache_file}{suffix}"

    def stub_dir(self, target: Any, /, **tkw: _U[ModulDirInput]) -> Path:
        """
        Prepare the _stubs directory for a package, module, or Path

        Ignore additional kwargs and set defaults:

        - package: None
        - subfolder: _stub
        """  # MOVE: header on port.config.Config protocol
        root: Path = ModuleGuard.root(target, tkw.get("package"))
        return PathGuard.dir(root / tkw.get("subfolder", "_stub"))

    def stub_file(
        self, target: Any, /, prefix: str, **tkw: _U[ModulFullInput]
    ) -> Path:
        """
        Create Single StubFile Path and ensure Backup and Writable

        Forward kwargs and set default for backup: None == False
        """  # MOVE: header on port.config.Config protocol

        stub_dir: Path = self.stub_dir(target, **tkw)
        stub_name = f"_{prefix.lower()}.pyi"  # CHECK: something after prefix?
        # LATER: add stub_name to self._names
        stub_file: Path = stub_dir / stub_name

        return PathGuard.backup(stub_file) if tkw.get("backup") else stub_file

    def init_stub_file(self, target: Any, /, **tkw: _U[ModulInitInput]) -> Path:
        """
        Create __init__ Stub File Path and ensure Backup and Writable

        Forward kwargs and set default for backup: None == False
        """  # MOVE: header on port.config.Config protocol

        stub_dir: Path = self.stub_dir(target, subfolder="", **tkw)
        stub_file: Path = stub_dir / "__init__.pyi"

        return PathGuard.backup(stub_file) if tkw.get("backup") else stub_file
