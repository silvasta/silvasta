"""
Find project root with pyproject.toml and extract data

- Transfrom to SimpleNamespace with dot access
- Jump to any section or value but try to avoid AttributeErrors

                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "pyproject_path",
    "load_toml",
    "pyproject_toml",
    "pyproject_sns",
    "dict_to_sns",
    "pyproject_name",
    "pyproject_version",
    "pyproject_log_section",
]

import tomllib
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Self

from loguru import logger

from ...port.config import ProjectInformation
from ...system.config import HomeSetup
from ._search import get_project_root


@dataclass
class ProjectInfo:
    """Check toml to provide Config and Printer with Info"""

    name: str = "sstcore"
    version: str = "0.0.0"

    @classmethod
    def collect(cls, home_setup, name: str | None = None) -> Self:
        try:
            name: str = name or pyproject_name()
            info: Self = cls(name=name or pyproject_name())
        except Exception as error:
            if home_setup == HomeSetup.GLOBAL:
                raise RuntimeError("Project Name Missing!") from error
        return info._update_version()

    def _update_version(self) -> Self:
        try:
            if project_version := version(distribution_name=self.name):
                self.version: str = project_version
        except PackageNotFoundError:
            logger.warning(
                f"Package '{self.name}' not installed in this environment. "
                "Are you running in dev mode without 'uv tool install -e .'?"
            )
        return self


if TYPE_CHECKING:
    _instance_check: ProjectInformation = ProjectInfo()
    _class_check: type[ProjectInformation] = ProjectInfo


def pyproject_path() -> Path:
    """Path to own pyproject.toml file"""
    return get_project_root(indicator="pyproject.toml") / "pyproject.toml"


@lru_cache(maxsize=1)
def load_toml(toml_path: Path) -> dict:
    """Reads and caches toml file as nested dict"""
    if not toml_path.exists():
        raise FileNotFoundError(f"Invalid {toml_path=}")
    with open(toml_path, "rb") as file:
        return tomllib.load(file)


@lru_cache(maxsize=1)
def pyproject_toml(pyproject_toml_path: Path | None = None) -> dict:
    """Read and cache pyproject.toml from path or try recursive path search"""
    path_to_load: Path = pyproject_toml_path or pyproject_path()
    return load_toml(path_to_load)


def pyproject_sns(pyproject_toml_path: Path | None = None) -> SimpleNamespace:
    """Transform pyproject.toml into SimpleNamespace with dot access"""
    toml: dict = pyproject_toml(pyproject_toml_path)
    return dict_to_sns(toml)


def dict_to_sns(data):  # LATER: move somewhere else if ever needed again
    """Transform nested dict to SimpleNamespace with dot access"""
    if isinstance(data, dict):
        # Recursive conversion of dict to unpack all nested values
        return SimpleNamespace(**{k: dict_to_sns(v) for k, v in data.items()})
    elif isinstance(data, list):
        # Recursive conversion of lists in case they contain dicts
        return [dict_to_sns(i) for i in data]
    else:
        return data


def pyproject_name(pyproject_toml_path: Path | None = None) -> str:
    """Fetches project metadata from: [project] in pyproject.toml"""
    pyproject_file: SimpleNamespace = pyproject_sns(pyproject_toml_path)
    return pyproject_file.project.name


def pyproject_version(pyproject_toml_path: Path | None = None) -> str:
    """Fetches project metadata from: [project] in pyproject.toml"""
    pyproject_file: SimpleNamespace = pyproject_sns(pyproject_toml_path)
    return pyproject_file.project.version


def pyproject_log_section(
    pyproject_toml_path: Path | None = None,
) -> SimpleNamespace:
    """Fetches from: [tool.sstcore.logging] in pyproject.toml"""
    pyproject: SimpleNamespace = pyproject_sns()
    tool_project_section: SimpleNamespace = getattr(
        pyproject.tool, pyproject_name(pyproject_toml_path)
    )
    return tool_project_section.logging
