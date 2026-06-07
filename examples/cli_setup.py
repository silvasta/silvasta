from pathlib import Path

from sstcore import printer
from sstcore.cli import SafeTyper, logger_catch, utils_app
from sstcore.config import ConfigSetupParam, get_config

example_setup_param = ConfigSetupParam(
    config_file=Path("my_config.json"),
    project_name="sstcore-lib",
    project_version="0.0.33",
)


def main():
    """Run the loaded and assembled Typer CLI"""
    app()


printer.title("Example Setup Param")
printer(example_setup_param)


printer.title("Defaults generated from ConfigManager")
nice_defaults: ConfigSetupParam = get_config().setup_info
printer(nice_defaults)


app = SafeTyper(
    name="robot",
    help="CLI for launching Robot Tasks",
    param=nice_defaults,
)


@app.command("launch")
@logger_catch
def launch_some_robo_stuff():
    """Insert new task here..."""
    for _ in range(5):
        printer("robo")


app.add_typer(utils_app)

if __name__ == "__main__":
    main()
