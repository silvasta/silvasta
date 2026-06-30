from pathlib import Path
from typing import cast

import typer

from ..utils import HomeSetup, PathGuard, day_count, printer
from ..utils.paint import ColorBox
from .defaults import SstDefaults
from .names import ParsedName, SstNames

summary_file = ParsedName(  # MOVE: but where?
    pattern="{day}_summary.{suffix}",
    keys=["day", "suffix"],
)


class SstPaths[TNames: SstNames, TDefaults: SstDefaults]:
    """Generates paths with the provided Names and Defaults"""

    def __init__(
        self,
        names: TNames | None = None,
        defaults: TDefaults | None = None,
        homes: HomeSetup = HomeSetup.PROJECT,
    ):
        self._defaults: TDefaults = defaults or cast(TDefaults, SstDefaults())
        self._names: TNames = names or cast(TNames, SstNames())
        self._homes: HomeSetup = homes

    @property
    @PathGuard.dir
    def project_root(self) -> Path:
        return self._homes.root

    @property
    @PathGuard.dir
    def configs_dir(self) -> Path:
        return self._homes.configs_dir

    @property
    @PathGuard.dir
    def log_dir(self) -> Path:
        return self._homes.log_dir

    @property
    @PathGuard.dir
    def data_dir(self) -> Path:
        return self.project_root / self._names.data_dir

    @property
    @PathGuard.dir
    def plot_dir(self) -> Path:
        return self.project_root / self._names.plot_dir

    @property
    @PathGuard.dir
    def data_home(self) -> Path:
        return self._homes.data_home

    @property
    @PathGuard.dir
    def state_home(self) -> Path:
        return self._homes.state_home

    @property
    @PathGuard.dir
    def config_home(self) -> Path:
        return self._homes.config_home

    def dot_env(self) -> Path:
        """Ensure .env File, create template for missing and raise"""
        try:
            return PathGuard.file(
                target=self.dot_env_unconfirmed,
                default_content=self._defaults.dot_env_content,
            )
        except FileNotFoundError:
            # MOVE: to pathguard error handling, or cli,
            #         - but with __rich__ cli print
            c: ColorBox = ColorBox.with_mode("bold")
            text = (
                f"{c.red('Missing .env File!')}"
                f" {c.white(self.dot_env_unconfirmed)}"
            )
            printer.danger(text)
            raise typer.Exit(code=1) from None

    @property
    def dot_env_unconfirmed(self) -> Path:
        """Provide bare dot_env Path without any checks"""
        return self.config_home / ".env"

    def scanner_cache_file(self, scan_root: Path) -> Path:
        return scan_root / ".sst_scanner_cache.json"

    @PathGuard.unique(ensure_parent=True)
    def summary_file(self, suffix: str = "md") -> Path:
        return self.data_dir / summary_file(
            {"day": str(day_count()), "suffix": suffix}
        )
