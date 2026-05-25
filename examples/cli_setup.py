import typer
from loguru import logger

logger.remove()  # Intercept noisy logs (until log setup in attach_callback)

from sstcore import printer  # noqa: E402
from sstcore.cli import attach_callback, logger_catch, utils_app  # noqa: E402
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
    name="robot",
    help="CLI for launching Robot Tasks",
    no_args_is_help=True,
)
# attach_callback(app, param=example_setup_param)
attach_callback(app, param=nice_defaults)


@app.command("launch")
@logger_catch
def launch_some_robo_stuff():
    """Insert new task here..."""
    for _ in range(5):
        printer("robo")


# utils
app.add_typer(utils_app)

if __name__ == "__main__":
    main()
