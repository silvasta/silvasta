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
]

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Self

from loguru import logger

from ...port.config import Homes, HomeSetup
from ...port.link import portlink
from ...util.path import HomeDirs, find_project_root


@portlink(Homes)
@dataclass
class SstHomes(HomeDirs):
    setup: HomeSetup

    @classmethod
    def from_setup(
        cls,
        setup: HomeSetup,
        /,
        root: Path | None = None,
        name: str | None = None,
        dirs: HomeDirs | None = None,
    ) -> Self:
        match setup:
            case HomeSetup.GLOBAL:
                if name:
                    return cls(**asdict(HomeDirs.at_global(name)), setup=setup)
                fail_reason = "global setup needs project name..."

            case HomeSetup.PROJECT:
                return cls(**asdict(HomeDirs.at_project(root)), setup=setup)

            case HomeSetup.LOCAL:
                return cls(**asdict(HomeDirs.at_local(root)), setup=setup)

            case HomeSetup.CUSTOM:
                if dirs:
                    return cls(**asdict(dirs), setup=setup)
                fail_reason = "custom setup needs defined dirs..."

        raise RuntimeError(f"Bad home setup, {fail_reason}")


#  LINE: -- Alternative? -- -- - -- -- - -- -- - -- -- - -- -- - -- --


DEFAULT_APP_NAME = "sstcore"


@portlink(Homes)
@dataclass
class _SstHomes(HomeDirs):
    # NEXT: check if fallback is needed/desired, otherwise delete
    setup: HomeSetup

    @classmethod
    def from_setup(
        cls,
        setup: HomeSetup,
        /,
        root: Path | None = None,
        name: str | None = None,
        dirs: HomeDirs | None = None,
    ) -> Self:
        resolved_name: str = name or DEFAULT_APP_NAME

        match setup:
            case HomeSetup.PROJECT:
                resolved_root = root or find_project_root()
                if resolved_root is not None:
                    return cls(
                        **asdict(HomeDirs.at_project(resolved_root)),
                        setup=setup,
                    )
                logger.debug(
                    "No pyproject.toml found for PROJECT setup; falling back to GLOBAL setup."
                )
                return cls(
                    **asdict(HomeDirs.at_global(resolved_name, Path.cwd())),
                    setup=HomeSetup.GLOBAL,
                )

            case HomeSetup.GLOBAL:
                return cls(
                    **asdict(HomeDirs.at_global(resolved_name, root)),
                    setup=setup,
                )

            case HomeSetup.LOCAL:
                return cls(**asdict(HomeDirs.at_local(root)), setup=setup)

            case HomeSetup.CUSTOM:
                if dirs:
                    return cls(**asdict(dirs), setup=setup)
                raise RuntimeError(
                    "Bad home setup, custom setup needs defined dirs..."
                )
