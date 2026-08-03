"""
Compose and Ensure Paths independent of system or location

- Assemble from Defaults, Names, HomeSetup and any desired input
- Use PathGuard to ensure existence, uniqueness or writability
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "SstPaths",
]

from pathlib import Path
from typing import TYPE_CHECKING

from ..port.config import Defaults, Homes, Names, Paths
from ..utils import PathGuard
from ._defaults import SstDefaults
from ._homes import HomeSetup, SstHomes
from ._names import SstNames


class SstPaths:
    """Generate paths with the provided Names and Defaults"""

    def __init__(
        self,
        defaults: Defaults | None = None,
        names: Names | None = None,
        homes: Homes | None = None,
    ):
        self._defaults: Defaults = defaults or SstDefaults()
        self._names: Names = names or SstNames()
        self._homes: Homes = homes or SstHomes.from_setup(HomeSetup.GLOBAL)

    @property
    @PathGuard.dir
    def project_root(self) -> Path:
        return self._homes.root

    @property
    @PathGuard.dir
    def config_dir(self) -> Path:
        return self._homes.config

    @property
    @PathGuard.dir
    def log_dir(self) -> Path:
        return self._homes.log

    @property
    @PathGuard.dir
    def data_dir(self) -> Path:
        return self._homes.data

    @property
    @PathGuard.dir
    def plot_dir(self) -> Path:
        return self.project_root / self._names.plot_dir

    @property
    @PathGuard.dir
    def state_dir(self) -> Path:
        return self._homes.state

    def dot_env(self) -> Path:
        """Ensure .env File, create template for missing and raise"""
        return PathGuard.file(
            target=self.dot_env_unconfirmed,
            default_content=self._defaults.dot_env_content,
        )

    @property
    def dot_env_unconfirmed(self) -> Path:
        """Provide bare dot_env Path without any checks"""
        return self.config_dir / ".env"

    def scanner_cache_file(self, scan_root: Path | None = None) -> Path:
        """Provide location for Scanner state data"""
        return (scan_root or self.state_dir) / self._names.scanner_cache_file

    @PathGuard.unique(ensure_parent=True)
    def summary_file(self, suffix: str = "md") -> Path:
        filename: str = self._names.summary_file(suffix=suffix)
        return self.data_dir / filename


if TYPE_CHECKING:
    _instance_check: Paths = SstPaths()
    _class_check: type[Paths] = SstPaths
