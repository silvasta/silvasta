from pathlib import Path

from pydantic import Field

from sstcore import PathGuard
from sstcore.config import (
    ConfigManager,
    SstDefaults,
    SstNames,
    SstPaths,
    SstSettings,
)
from sstcore.utils import printer

# TASK: refresh this!


class Names(SstNames):
    """Define new custom names or override default names,
    used in Paths and to access them by config.{some_name}"""

    report_dir: str = "reports"


class Defaults(SstDefaults):
    print_value: int = 5


class Settings(SstSettings):
    names: Names = Field(default_factory=Names)
    defaults: Defaults = Field(default_factory=Defaults)


class Paths(SstPaths):
    @property
    @PathGuard.dir
    def report_dir(self) -> Path:
        return Path.cwd() / self._names.data_dir

    @property
    def report_file(self) -> Path:
        return self.report_dir / "example.pdf"


config: ConfigManager[Settings, Names, Defaults, Paths] = ConfigManager(
    settings_cls=Settings,
    paths_cls=Paths,
    project_name="MyProject",
    setting_file=Path.cwd() / "example_settings.json",
)

printer.success("config is ready!")
printer(config.settings)

config.paths.report_dir.touch()

for i in range(config.defaults.print_value):
    printer.success(f"Success {i}")
