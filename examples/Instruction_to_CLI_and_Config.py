from pathlib import Path

from pydantic import Field

from sstcore import PathGuard
from sstcore.cli import SafeTyper, utils_app
from sstcore.cli.launch import launch_folder_scanner, launch_monitor
from sstcore.config import (
    ConfigManager,
    SstDefaults,
    SstNames,
    SstPaths,
    SstSettings,
)
from sstcore.config.loader import sst_config, sst_config_loader
from sstcore.exceptions import TuiSelectorError
from sstcore.utils import printer

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Example and Instruction: Setup Custom Config and CLI
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Config Base Parts
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Names(SstNames):
    """Hold pattern, schemas, static and parsed names"""

    report_dir: str = "reports"


class Defaults(SstDefaults):
    """Hold app config, debug or even user params"""

    print_value: int = 5


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### The (independent) Intermediates
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class Paths(SstPaths[Names, Defaults]):
    """Provide assembled and optional ensured dynamic Paths"""

    @property
    @PathGuard.dir
    def report_dir(self) -> Path:
        return Path.cwd() / self._names.data_dir

    @property
    def report_file(self) -> Path:
        return self.report_dir / "example.pdf"


class Settings(SstSettings):
    """Assemble everything and provide the json"""

    names: Names = Field(default_factory=Names)
    defaults: Defaults = Field(default_factory=Defaults)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### The Manager
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

type CustomConfig = ConfigManager[Settings, Names, Defaults, Paths]


def config_loader(setting_file: Path | None = None) -> CustomConfig:
    """Prepare Loader for CustomConfig injected to CLI"""

    return sst_config_loader(
        settings_cls=Settings,
        paths_cls=Paths,
        setting_file=setting_file,
        project_name="sachmis",
    )


def config() -> CustomConfig:
    """Fetch config Singleton and raise if not already initialized"""
    return sst_config(_allow_uninitialized=False)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### config() Examples
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

printer.special(f"{config()} is Ready!")

printer(config().settings)

config().paths.report_file.touch()

for i in range(config().defaults.print_value):
    printer.success(f"Success {i}")


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### The CLI
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Create SafeTyper and assemble Functions
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

app = SafeTyper(
    name="custom",
    help="Dont forget the config loader!",
    config_loader=config_loader,
)

# Attach Single Commands (as well recommended with decorator)
app.command(name="scanner")(launch_folder_scanner)
app.command(name="monitor")(launch_monitor)


# Attach SubApp with new Level of Namespace
app.add_typer(typer_instance=utils_app)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Prepare Error Handler and attach to SafeTyper
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def attach_handlers(app: SafeTyper) -> None:
    """Assemble Handler in separate file and attach to app with this"""

    @app.register_error_handler(TuiSelectorError)
    def handle_tui_selector(error: TuiSelectorError):
        printer.danger(f"Selector failed: {error}")


# Execute this in same file as app is created
attach_handlers(app)

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Launch! recommended in project.__main__ or cli topfolder
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def main():
    app()


if __name__ == "__main__":
    main()
