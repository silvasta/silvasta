from collections.abc import Callable
from dataclasses import asdict, dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Self

from loguru import logger

from .homes import HomeSetup
from .settings import SstSettings


@dataclass
class BootResult:
    """Final confirmed Result by ConfigBootstrap"""

    project_name: str
    project_version: str
    setting_file: Path


@dataclass
class BootDefaults:
    """Input Args for ConfigBootstrap"""

    home_setup: HomeSetup
    project_name: str = ""
    project_root_indicator: str = "pyproject.toml"
    project_root: Path | None = None
    project_version: str = "0.0.0"

    setting_file: Path | None = None
    setting_file_name: str = "settings.json"


class DefaultBootPaths(BootDefaults):
    """Helper for Lazy Path loading, holds Sorting of Path execution"""

    def provided_setting_file(self) -> Path:
        if self.setting_file:
            return self.setting_file
        raise FileNotFoundError("No setting file provided in BootDefaults")

    def provided_from_home_setup(self) -> Path:
        return self.home_setup.configs_dir / self.setting_file_name

    def _home_setup_path(self, target: HomeSetup):
        if self.home_setup == target:
            # AI: usually that should not happen, still...
            raise ValueError("This path is already 'provided_from_home_setup'")
        return target.configs_dir / self.setting_file_name

    def home_setup_project(self) -> Path:
        return self._home_setup_path(target=HomeSetup.PROJECT)

    def home_setup_global(self) -> Path:
        return self._home_setup_path(target=HomeSetup.GLOBAL)

    def home_setup_local(self) -> Path:
        return self._home_setup_path(target=HomeSetup.LOCAL)

    @classmethod
    def path_factory(cls, defaults: BootDefaults) -> list[Callable[..., Path]]:
        factory: Self = cls(**asdict(defaults))
        return [
            factory.provided_setting_file,
            factory.provided_from_home_setup,
            factory.home_setup_project,
            factory.home_setup_global,
            factory.home_setup_local,
        ]


class ConfigBootstrap[TSettings: SstSettings]:
    """Collection of methods that run before config is ready"""

    @classmethod
    def initial_setup(
        cls, settings_cls: type[TSettings], defaults: BootDefaults
    ) -> BootResult:

        # LATER: check if needed at all or validation needed
        project_name: str = defaults.project_name
        version: str = (
            cls.check_project_version(package_name=defaults.project_name)
            or defaults.project_version
        )
        HomeSetup(defaults.home_setup).boot(
            project_name=project_name,
            project_root_indicator=defaults.project_root_indicator,
            project_root=defaults.project_root,
        )
        for path in DefaultBootPaths.path_factory(defaults):
            if final_setting_file := cls.check_location(path, settings_cls):
                logger.info(f"Found valid Settings: {final_setting_file=}")
                break
        else:
            # AUTO-SCAFFOLD: create default config at the project location
            default_path: Path = cls._scaffold_default_config(settings_cls)
            logger.warning(
                f"No existing Settings found — created scaffold: {default_path=}"
            )
            final_setting_file: Path = default_path

        return BootResult(
            project_name=defaults.project_name,
            project_version=version,
            setting_file=final_setting_file,
        )

    @staticmethod
    def check_location(
        path_function: Callable, settings_cls: type[TSettings]
    ) -> Path | None:
        """Verify if SettingsFile exists at path and can be loaded"""
        try:
            path: Path = path_function()
            if not path.exists():
                raise FileNotFoundError
            settings_cls.load(path)
            logger.info(f"Found valid SettingsFile at {path=}")
            return path

        except FileNotFoundError as error:
            logger.debug(f"No file found at {path=}, {error=}")
        except ValueError as error:
            # AI: ...is this ValueError warning to hard for doubled _home_setup_path?
            logger.warning(
                f"Problem with loading SettingsFile: {path=}, {error=}"
            )
        return None

    @classmethod
    def _scaffold_default_config(
        cls, settings_cls, defaults: BootDefaults
    ) -> Path:
        """Create a minimal valid config. Never overwrite existing."""

        for path_function in DefaultBootPaths.path_factory(defaults):
            try:
                if (path := path_function()).exists():
                    raise FileExistsError(f"Detected Existing File! {path=}")

                path.parent.mkdir(parents=True, exist_ok=True)
                settings_cls().save(path)
                logger.info("New setting file created from defaults")
                return path

            except FileNotFoundError:
                logger.debug(f"Path can't be constructed: {path=}")

            except ValueError as error:
                logger.warning(f"Problem with: {path=}, {error=}")

        raise RuntimeError("Unable to scaffold new setting file")

    @staticmethod
    def check_project_version(package_name) -> str | None:
        """Get project_version from installation with project_name"""
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
