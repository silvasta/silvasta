import typer
from loguru import logger

logger.remove()  # Intercept noisy logs (until log setup in attach_callback)

from sstcore import printer  # noqa: E402
from sstcore.cli import attach_callback, command  # noqa: E402
from sstcore.config import ConfigSetupParam, get_config  # noqa: E402

example_setup_param = ConfigSetupParam(
    log=None,  # using bare defaults
    config_file="my_config.json",  # highly recommended not hardcoding this!
    project_name="sstcore-lib",
    project_version="0.0.33",
)
printer.title("Example Setup Param")
printer(example_setup_param)


nice_defaults: ConfigSetupParam = get_config().compose_setup_param()

printer.title("Nice automatically generated Defaults")
printer(nice_defaults)


def main():
    app()


# main
app = typer.Typer(
    name="singu",
    help="CLI for launching Robot or Development Tasks",
    no_args_is_help=True,
)
# attach_callback(app, param=example_setup_param)
attach_callback(app, param=nice_defaults)


# utils
app.command("monitor")(command.launch_monitor)
app.command("scanner")(command.folder_scanner)
app.command("config")(command.config_details)

if __name__ == "__main__":
    main()
