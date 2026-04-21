import json
import os
from datetime import UTC, datetime, timedelta
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Self, cast

from dotenv import load_dotenv
from loguru import logger

from silvasta.utils import day_count
from silvasta.utils.log import LogParam
from silvasta.utils.print import Printer

from .defaults import SstDefaults
from .names import SstNames
from .paths import SstPaths
from .settings import SstSettings

type ConfigTypes = SstDefaults | SstNames | SstPaths | SstSettings


class ConfigManager[
    TSettings: SstSettings,
    TNames: SstNames,
    TDefaults: SstDefaults,
    TPaths: SstPaths,
]:
    """Provide singleton with all settings and factories"""

    _env_loaded = False

    def __init__(
        self,
        settings_cls: type[TSettings],
        paths_cls: type[TPaths],
        write_new_master_setting_file_if_missing: bool = True,
    ):
        self._starttime: datetime = datetime.now(UTC)

        self._settings_cls: type[TSettings] = settings_cls
        self._paths_cls: type[TPaths] = paths_cls
        logger.debug(f"Attached {self._s_class} and {self._p_class}")

        self._ensure_master_setting_file(
            write_new_master_setting_file_if_missing
        )
        self.setting_file: Path = self._find_setting_file()
        logger.debug("setting_file ready")

        self.settings: TSettings = self._load_settings()
        self.paths: TPaths = self._load_paths()
        self._log_types_of_all_classes()

        self.project_name: str = self._check_project_name()
        self.project_version: str = self._check_project_version()
        self._fill_printer()

        self.defaults.home_setup.boot(
            local_home_root=self.paths.local_home_dir,
            project_name=self.project_name,
        )

    @classmethod
    def default_setup(
        cls, write_new_master_setting_file_if_missing=False
    ) -> Self:
        return cls(
            settings_cls=SstSettings,
            paths_cls=SstPaths,
            write_new_master_setting_file_if_missing=write_new_master_setting_file_if_missing,
        )

    def save_settings(self):
        self.settings.save_to_path(self.setting_file)
        # REMOVE: redundant save, but first handle Task: setting_files
        self.settings.save_to_master_setting_file()
        logger.info(f"Settings saved to: {self.setting_file}")

    def load_settings_from_path(self, path: Path | None = None) -> TSettings:
        """Create TSettings instance from setting_file or master_setting_file"""
        if not (setting_file := path or self.master_setting_file).exists():
            raise FileNotFoundError(f"Invalid path: {setting_file=}")

        settings: TSettings = self._settings_cls.model_validate(
            json.loads(setting_file.read_text(encoding="utf-8"))
        )
        logger.debug(f"Loaded {self._s_class} from {setting_file=}")
        return settings

    def _load_settings(self) -> TSettings:
        return self.load_settings_from_path(self.setting_file)

    def _load_paths(self) -> TPaths:
        return self._paths_cls(names=self.names, defaults=self.defaults)

    def _find_setting_file(self) -> Path:
        # TASK: setting_files
        # - load master_setting_file first and read?
        # - look over all HomeSetup locatons?
        # when save to master_setting_file?
        # - for sure when HomeSetup changes
        # - what else?
        # strategy for setting_files
        # - master_setting_file 1:1 copy of setting_file?
        # - or even master_setting_file is setting_file?
        # what about local_setting_files?
        # - create local config in .camp/local.json?
        return self.master_setting_file

    def _ensure_master_setting_file(
        self, write_new_master_setting_file_if_missing: bool
    ):
        """TSettings ensured existence or generated default"""
        # REMOVE: not storing as attribute? only ensure here?
        self.master_setting_file: Path = self._settings_cls.ensure_master_setting_file(
            write_new_file_if_missing=write_new_master_setting_file_if_missing
        )

    def _check_project_name(self) -> str:
        """Get project_name from Names or fallback to Defaults"""
        if self.names.project:
            project_name: str = self.names.project
            logger.debug(f"using {project_name=}")
            return project_name
        else:
            default_name: str = self.defaults.project_name
            logger.warning(f"No project_name defined, using: {default_name=}")
            return default_name

    def _check_project_version(self, version_str: str | None = None):
        """Get project_version from installation with project_name"""
        try:
            project_version: str = version(self.project_name)
        except PackageNotFoundError:
            logger.warning(
                f"Package '{self.project_name}' not installed in this environment. "
                "Are you running in dev mode without 'pip install -e .'?"
            )
            project_version: str = self.defaults.project_version_fallback

        return project_version if version_str is None else version_str

    def _fill_printer(self):
        Printer.project_name = self.project_name
        Printer.project_version = self.project_version

    @property
    def names(self) -> TNames:
        """Explicit return of Generic type with dot access"""
        return cast(TNames, self.settings.names)

    @property
    def defaults(self) -> TDefaults:
        """Explicit return of Generic type with dot access"""
        return cast(TDefaults, self.settings.defaults)

    @property
    def _s_class(self) -> str:
        """Get name of SstSettings derivative out of TSettings class"""
        return self._settings_cls.__name__

    @property
    def _p_class(self) -> str:
        """Get name of SstPaths derivative out of TPaths class"""
        return self._paths_cls.__name__

    @property
    def all_instances(self) -> list[ConfigTypes]:
        return [
            self.paths,
            self.settings,
            self.names,
            self.defaults,
        ]

    def _log_types_of_all_classes(self):
        active_instance_types: str = " - ".join(
            type(instance).__name__ for instance in self.all_instances
        )
        logger.debug(f"{active_instance_types=}")

    @property
    def dom(self) -> int:
        return day_count()

    @property
    def starttime(self) -> str:
        return self._starttime.strftime(self.defaults.timestamp_format)

    @property
    def duration(self) -> timedelta:
        # LATER: where and how to apply format?
        return datetime.now(UTC) - self._starttime

    @property
    def timestamp(self) -> str:
        return datetime.now(UTC).strftime(self.defaults.timestamp_format)

    def from_env(self, key: str):
        """get variable from environment, log failure, raise error"""
        if not self._env_loaded:
            load_dotenv(self.paths.dot_env)
            self._env_loaded = True
        var: str = os.getenv(key, "fail")  # NOTE: stable enough?
        if var == "fail":
            logger.error(f"failed to load env var with {key=}")
            raise ValueError("Value not found in os.env or with loaded .env")
        return var

    def compose_setup_param(self) -> dict[str, str | LogParam]:
        return {
            # utils.setup_logging
            "log": LogParam(
                log_dir=self.names.log_dir,
                log_filename=self.names.log_file,
                log_level=self.defaults.log.level,
                retention=self.defaults.log.retention,
                rotation=self.defaults.log.rotation,
            ),
            # cli.setup
            "config_file": str(self.setting_file),
        }
