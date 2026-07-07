# TODO: explain

import tomllib
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

from .search import get_project_root


def pyproject_path() -> Path:
    """Path to own pyproject.toml file"""
    return get_project_root(indicator="pyproject.toml") / "pyproject.toml"


@lru_cache(maxsize=1)
def pyproject_toml(pyproject_toml_path: Path | None = None) -> dict:
    """Read and cache pyproject.toml from path or try recursive path search"""
    path_to_load: Path = pyproject_toml_path or pyproject_path()
    return load_toml(path_to_load)


@lru_cache(maxsize=1)
def load_toml(toml_path: Path) -> dict:
    """Reads and caches toml file as nested dict"""
    if not toml_path.exists():
        raise FileNotFoundError(f"Invalid {toml_path=}")
    with open(toml_path, "rb") as file:
        return tomllib.load(file)


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
