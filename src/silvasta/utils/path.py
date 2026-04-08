import os
import tomllib
from enum import StrEnum, auto
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace


class XdgHomes(StrEnum):
    DATA = auto()
    STATE = auto()
    CONFIG = auto()

    @property
    def path(self) -> Path:
        return Path(
            os.getenv(
                key=f"XDG_{self.name}_HOME",
                default=self._default_path(),
            )
        )

    def _default_path(self) -> Path:
        """Default to user home and default location"""
        mapping: dict = {
            XdgHomes.DATA: ".local/share",
            XdgHomes.STATE: ".local/state",
            XdgHomes.CONFIG: ".config",
        }
        return Path.home() / mapping[self]


def recursive_root(path: Path, indicator: str) -> Path | None:
    """Find root by indicator iterating parent paths upwards"""
    if (path / indicator).exists():
        return path
    elif path == path.parent:
        return None
    else:
        return recursive_root(path.parent, indicator)


def recursive_parent(path: Path, parent_dir_name: str) -> Path | None:
    """Find closest parent dir with name by iterating upwards"""
    if path.parent.name == parent_dir_name:
        return path
    elif path == path.parent:
        return None
    else:
        return recursive_parent(path.parent, parent_dir_name)


def find_project_root(indicator: Path | str = "pyproject.toml") -> Path:
    """Call recursive root function, return Success, Error for fail"""

    search_result: Path | None = recursive_root(Path.cwd(), str(indicator))

    if search_result:
        return search_result
    else:
        print(f"Failed with indicator: {indicator}")
        raise FileNotFoundError("Project root not found!")


def pyproject_path() -> Path:
    """Path to own pyproject.toml file"""

    return find_project_root(indicator="pyproject.toml") / "pyproject.toml"


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
    """Transform pyproject.toml into SimpleNamespace with dot acces"""
    toml: dict = pyproject_toml(pyproject_toml_path)
    return dict_to_sns(toml)


def dict_to_sns(data: dict):
    """Transform nested dict to SimpleNamespace with dot acces"""
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
    """Fetches from: [tool.silvasta.logging] in pyproject.toml"""
    pyproject: SimpleNamespace = pyproject_sns()
    tool_project_section: SimpleNamespace = getattr(
        pyproject.tool, pyproject_name(pyproject_toml_path)
    )
    return tool_project_section.logging
