"""
Example and Instruction: Setup Custom Config and CLI

- Config
- SafeTyper
- SYSTEM
"""

# TODO: 4/5 show full pipeline!
# NEXT: add system
# - use sachmis as example

from pathlib import Path

from pydantic import Field

from sstcore import PathGuard, printer
from sstcore.console import SafeTyper
from sstcore.console.tools import cli_tools
from sstcore.console.tools._app import (
    launch_folder_scanner,
    launch_log_monitor_2,
)
from sstcore.error import TuiSelectorError
from sstcore.port import config
from sstcore.port.link import portlink
from sstcore.system.boot import (
    sst_config_loader,
    sst_system_loader,
)
from sstcore.system.config import (
    ConfigManager,
    SstDefaults,
    SstNames,
    SstPaths,
    SstSettings,
)

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Config Base Parts
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@portlink(config.Names)
class Names(SstNames):
    """Hold pattern, schemas, static and parsed names"""

    report_dir: str = "reports"


@portlink(config.Defaults)
class Defaults(SstDefaults):
    """Hold app config, debug or even user params"""

    print_value: int = 5


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### The (independent) Intermediates
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@portlink(config.Paths)
class Paths(SstPaths):
    """Provide assembled and optional ensured dynamic Paths"""

    @property
    @PathGuard.dir
    def report_dir(self) -> Path:
        return Path.cwd() / self._names.data_dir

    @property
    def report_file(self) -> Path:
        return self.report_dir / "example.pdf"


@portlink(config.Settings)
class Settings(SstSettings):
    """Assemble everything and provide the json"""

    names: Names = Field(default_factory=Names)
    defaults: Defaults = Field(default_factory=Defaults)


type CustomConfig = ConfigManager[Defaults, Names, Paths, Settings]


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Create SafeTyper and assemble Functions
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

app = SafeTyper(
    name="custom",
    help="Dont forget the config loader!",
    system_loader=sst_system_loader(
        config_loader=sst_config_loader(
            settings_cls=Settings,
            paths_cls=Paths,
            project_name="sachmis",
        )
    ),
)

# Attach Single Commands (as well recommended with decorator)
app.command(name="scanner")(launch_folder_scanner)
app.command(name="monitor")(launch_log_monitor_2)


# Attach SubApp with new Level of Namespace
app.add_typer(typer_instance=cli_tools)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Prepare Error Handler and attach to SafeTyper
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def attach_handlers(app: SafeTyper) -> None:
    """Assemble Handler in separate file and attach to app with this"""

    @app.errors.attach(exit_code=2, name="Tui Selector")
    def handle_tui_selector(error: TuiSelectorError):
        printer.danger(f"Selector failed: {error}")


# Execute this in same file as the app is created
attach_handlers(app)

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Launch! recommended in project.__main__ or cli topfolder
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def main():
    app()


if __name__ == "__main__":
    main()
