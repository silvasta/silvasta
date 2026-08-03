"""
Boot HomeDirs depending on Configuration and provide according Paths

- Global:
    Located at XDG_HOMES, e.g.:  ~/.config/NAME  or  ~/.local/share/NAME

- Project:
    Located at project root usually identified by pyproject.toml

- Local:
    Located at given path or usually CWD

Path composition according to schema below.
- In projects usually: root/data/*homes
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "HomeSetup",
    "SstHomes",
    "ProjectInfo",
]

from dataclasses import asdict, dataclass
from enum import StrEnum, auto
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import TYPE_CHECKING, Self

from loguru import logger

from ..port.config import Homes
from ..port.config import ProjectInfo as ProjectInfo_
from ..utils.path import HomeDirs, pyproject_name


class HomeSetup(StrEnum):
    GLOBAL = auto()
    PROJECT = auto()
    LOCAL = auto()
    CUSTOM = auto()


@dataclass
class SstHomes(HomeDirs):
    setup: HomeSetup

    @classmethod
    def from_setup(
        cls,
        setup: HomeSetup,
        root: Path | None = None,
        name: str | None = None,
        dirs: HomeDirs | None = None,
    ) -> Self:
        match setup:
            case HomeSetup.GLOBAL:
                if name:
                    return cls(**asdict(HomeDirs.at_global(name)), setup=setup)
                message = "global setup needs project name..."

            case HomeSetup.PROJECT:
                return cls(**asdict(HomeDirs.at_project(root)), setup=setup)

            case HomeSetup.LOCAL:
                return cls(**asdict(HomeDirs.at_local(root)), setup=setup)

            case HomeSetup.CUSTOM:
                if dirs:
                    return cls(**asdict(dirs), setup=setup)
                message = "custom setup needs defined dirs..."

        raise RuntimeError(f"Bad home setup, {message}")


@dataclass
class ProjectInfo:  # NEXT: sync with printer and port
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
        """Get project_version from installation with project_name"""
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
    _instance_check: Homes = SstHomes(**dict())
    _class_check: type[Homes] = SstHomes
    #
    _instance_check: ProjectInfo_ = ProjectInfo()
    _class_check: type[ProjectInfo_] = ProjectInfo
