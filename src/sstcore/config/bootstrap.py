from collections.abc import Callable
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from loguru import logger

from ..utils.path import XdgHomes, recursive_root
from .settings import SstSettings


@dataclass
class ProjectMeta:
    project_name: str
    project_version: str


class ConfigBootstrap[TSettings: SstSettings]:
    default_project_name: str = "sstcore"
    default_project_version: str = "0.0.0"

    default_setting_file_name: str = "settings.json"

    _provided_setting_file: Path | None = None
    _settings_cls: type[TSettings]

    @classmethod
    def ensure(
        cls,
        settings_cls: type[TSettings],
        project_name: str,
        setting_file: Path | None = None,
    ) -> Path:

        cls._settings_cls: type[TSettings] = settings_cls
        cls._provided_setting_file: Path | None = setting_file
        cls.default_project_name: str = project_name

        for path_loader in cls.target_locations():
            if final_setting_file := cls.check_location(path_loader):
                logger.info(f"{final_setting_file=}")
                return final_setting_file

        # AUTO-SCAFFOLD: create a default config at the project location
        default_path: Path = cls._scaffold_default_config(settings_cls)
        logger.warning(f"No config found — created scaffold at {default_path}")

        return default_path

    @classmethod
    def _scaffold_default_config(cls, settings_cls) -> Path:
        """Create a minimal valid config. Never overwrite existing."""
        # Prefer project-local configs/ dir if in a project
        if root := cls.find_project_setting_file():
            target: Path = root / "configs" / cls.default_setting_file_name
        else:
            target: Path = cls.xdg_config_path()

        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_text(
                settings_cls.default_json_content(), encoding="utf-8"
            )
        return target

    @classmethod
    def check_location(cls, path_loader: Callable) -> Path | None:
        try:
            if not (path := path_loader()):
                raise FileNotFoundError
            cls._settings_cls.load(path)
            logger.info("Found valid SettingsFile at path=")
            return path

        except FileNotFoundError as error:
            logger.debug(f"No file found at {path=}, {error=}")

        except ValueError as error:
            logger.warning(
                f"Problem with loading SettingsFile: {path=}, {error=}"
            )
        return None

    @classmethod
    def target_locations(cls) -> list[Callable[..., Path | None]]:
        return [
            cls.find_provided_setting_file,
            cls.find_project_setting_file,
            cls.find_global_setting_file,
            cls.find_local_setting_file,
        ]

    @classmethod
    def find_provided_setting_file(cls) -> Path | None:
        if path := cls._provided_setting_file:
            return cls._provided_setting_file
        logger.debug(f"No file found at {path=}")

    @classmethod
    def find_project_setting_file(cls) -> Path | None:
        if project_root := recursive_root(Path.cwd(), "pyproject.toml"):
            path = project_root / "configs" / cls.default_setting_file_name
            if path.exists():
                return path
        logger.debug(f"No file found at {path=}")

    @classmethod
    def find_global_setting_file(cls) -> Path | None:
        if path := cls.xdg_config_path():
            if path.exists():
                return path
        logger.debug(f"No file found at {path=}")

    @classmethod
    def xdg_config_path(cls) -> Path:
        return (
            XdgHomes(value="config").path_from_os()
            / cls.default_project_name
            / cls.default_setting_file_name
        )

    @classmethod
    def find_local_setting_file(cls) -> Path | None:
        # TASK: return only Path
        if (path := Path.cwd() / cls.default_setting_file_name).exists():
            return path
        logger.debug(f"No file found at {path=}")

    @classmethod
    def meta(cls):
        ensured_name: str = cls.check_project_name()
        ensured_version: str = cls.check_project_version(ensured_name)
        return ProjectMeta(
            project_name=ensured_name,
            project_version=ensured_version,
        )

    @classmethod
    def check_project_name(cls) -> str:
        """Get project_name from Names or fallback to Defaults"""
        if project_name := cls.default_project_name:
            logger.debug(f"using {project_name=}")
            return project_name
        else:
            default_name: str = cls.default_project_name
            logger.warning(f"No project_name defined, using: {default_name=}")
            return default_name

    @classmethod
    def check_project_version(
        cls, package_name, version_str: str | None = None
    ):
        """Get project_version from installation with project_name"""
        if version_str:
            return version_str

        try:
            project_version: str = version(package_name)
            return project_version
        except PackageNotFoundError:
            logger.warning(
                f"Package '{package_name}' not installed in this environment. "
                "Are you running in dev mode without 'uv tool install -e .'?"
            )
        except ValueError:
            logger.warning("No distribution name provided to check version")

        return cls.default_project_version
