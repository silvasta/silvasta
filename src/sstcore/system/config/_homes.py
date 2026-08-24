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

from sstcore.system.config import HomeSetup

__all__: list[str] = [
    "HomeSetup",
    "SstHomes",
]

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Self

from ...port.config import Homes
from ...util.path import HomeDirs


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


if TYPE_CHECKING:
    _instance_check: Homes = SstHomes(**dict())
    _class_check: type[Homes] = SstHomes
    #
