from pathlib import Path

from pydantic import Field

from silvasta.config import (
    ConfigManager,
    SstDefaults,
    SstNames,
    SstPaths,
    SstSettings,
)
from silvasta.utils import printer


class Names(SstNames):
    """Define new custom names or override default names,
    used in Paths and to acces them by config.{some_name}"""

    project: str = "sstcore"

    # Use same folder as example file to show usage
    data_dir: str = Path(__file__).resolve().parent.name
    user_setting_file: str = "example_settings.json"


class Defaults(SstDefaults):
    print_value: int = 5


class ProjectSettings(SstSettings):
    names: Names = Field(default_factory=Names)
    defaults: Defaults = Field(default_factory=Defaults)


class Paths(SstPaths):
    pass


config: ConfigManager[ProjectSettings, Names, Defaults, Paths] = ConfigManager(
    settings_cls=ProjectSettings,
    paths_cls=Paths,
    write_new_master_setting_file_if_missing=True,
)

# do you see: 'x: int'? (where ': int' comes from type checker)
x = config.defaults.print_value

for i in range(config.defaults.print_value):
    print(f"Success {i}")

printer(config.settings)
