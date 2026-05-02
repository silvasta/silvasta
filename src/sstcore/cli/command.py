from ..config import ConfigManager, get_config
from ..utils.print import printer
from . import monitor, sargs, scanner


def launch_monitor(file: sargs.File = None):  # NOTE: CLI hint not amazing...
    """Launch Log Console Monitor: watch new log file entries"""
    monitor(log_path=file)


def folder_scanner(
    scan_root: sargs.Root = None, output_file: sargs.File = None
):
    """Launch Folder Scanner with TreeSelector: write combined file"""
    scanner(scan_root, output_file)


def config_details():
    """Print config and paths to Console, use --write for new"""
    config: ConfigManager = get_config()

    printer(config.settings)
    printer(config.setting_file)

    # printer(config.paths.dot_env) INFO: raises Error and creates empty default if file not exists
