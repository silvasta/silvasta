from pydantic import Field
from silvasta.config.settings import BaseDefaults, BaseNames, BasePaths, Settings
from pathlib import Path

from silvasta.config.manager import ConfigManager


class Names(BaseNames):
    """Define new custom names or override default names,
    used in Paths and to acces them by config.{some_name}"""

    # Use same folder as example file to show usage
    data_dir: str = Path(__file__).resolve().parent.name
    user_setting_file: str = "example_settings.json"


class Defaults(BaseDefaults):
    print_value: int = 5


class ProjectSettings(Settings):
    names: Names = Field(default_factory=Names)
    defaults: Defaults = Field(default_factory=Defaults)


class Paths(BasePaths):
    pass


# TODO: example where config manager gets override?

config: ConfigManager[ProjectSettings, Names, Defaults, Paths] = ConfigManager(
    settings_cls=ProjectSettings,
    paths_cls=Paths,
    save_defaults_to_file=True,
)

# do you see: 'x: int'? (where ': int' comes from type checker)
x = config.defaults.print_value

for i in range(config.defaults.print_value):
    print(f"Success {i}")
