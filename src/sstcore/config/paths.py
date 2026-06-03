from pathlib import Path
from typing import cast

import typer
from loguru import logger

from ..utils import PathGuard, day_count
from ..utils.path import recursive_root
from ..utils.print import ColorBox, printer
from .defaults import HomeSetup, SstDefaults
from .names import AutoParsedName, ParsedName, SstNames

c: ColorBox = printer.colorbox()

# MOVE: but where?
summary_file: AutoParsedName = ParsedName(
    pattern="{day}_summary.{suffix}",
    keys=["day", "suffix"],
)


class SstPaths[TNames: SstNames, TDefaults: SstDefaults]:
    """Generates paths with the provided Names and Defaults"""

    def __init__(
        self,
        names: TNames | None = None,
        defaults: TDefaults | None = None,
    ):
        self._defaults: TDefaults = defaults or cast(TDefaults, SstDefaults())
        self._names: TNames = names or cast(TNames, SstNames())

        self.project_root: Path = self._check_local_root()

    def _check_local_root(self) -> Path:
        """Find project root or use CWD"""
        root: Path | None = recursive_root(
            path=Path.cwd(),
            indicator=self._defaults.project_root_indicator,
        )
        if root is not None:
            self.project_root_found = True

            return root

        if self._defaults.home_setup == HomeSetup.LOCAL:  # TEST: home switch
            logger.warning("No project root found -> default to: 'global'")
            self._defaults.home_setup = HomeSetup.GLOBAL

        self.project_root_found = False

        return Path.cwd()

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
    def log_dir(self) -> Path:
        return self.project_root / "logs"

    @property
    @PathGuard.dir
    def local_home_dir(self) -> Path:
        return self.data_dir / "homes"

    @property
    @PathGuard.dir
    def data_home(self) -> Path:
        return self._defaults.home_setup.data_home

    @property
    @PathGuard.dir
    def state_home(self) -> Path:
        return self._defaults.home_setup.state_home

    @property
    @PathGuard.dir
    def config_home(self) -> Path:
        return self._defaults.home_setup.config_home

    @property
    def dot_env(self) -> Path:
        try:
            return PathGuard.file(
                target=self.config_home / ".env",
                default_content=self._defaults.dot_env_content,
            )
        except FileNotFoundError:
            text = f"{c.red('Missing .env File!')} {c.white(self.dot_env_unconfirmed)}"
            printer.danger(text)
            raise typer.Exit(code=1) from None

    @property
    def dot_env_unconfirmed(self) -> Path:
        return PathGuard.file(
            target=self.config_home / ".env",
            default_content=self._defaults.dot_env_content,
            raise_error=False,
        )

    @PathGuard.unique(ensure_parent=True)
    def summary_file(self, suffix: str = "md") -> Path:
        return self.data_dir / summary_file(
            {"day": str(day_count()), "suffix": suffix}
        )
