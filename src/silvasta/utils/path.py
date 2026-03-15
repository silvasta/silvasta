import functools
import logging
import os
import re
import shutil
import tomllib
from collections.abc import Callable
from enum import Enum, auto
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import ParamSpec, overload

logger: logging.Logger = logging.getLogger(__name__)

P = ParamSpec("P")


class XdgHomes(Enum):
    DATA = auto()
    STATE = auto()
    CONFIG = auto()

    @property
    def path(self) -> Path:
        env_var_key = f"XDG_{self.name}_HOME"
        return Path(os.getenv(env_var_key, self._default_path()))

    def _default_path(self) -> Path:
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


def recursive_parent(path: Path, indicator: str) -> Path | None:
    """Find root by indicator iterating parent paths upwards"""
    if path.parent.name == indicator:
        logger.debug(f"Found {indicator=}")
        return path
    elif path == path.parent:
        logger.debug(f"Not found {indicator=}")
        return None
    else:
        return recursive_parent(path.parent, indicator)


def find_project_root(indicator: Path | str = "pyproject.toml") -> Path:
    """Call recursive function, return Success, Error for fail"""

    search_result: Path | None = recursive_root(Path.cwd(), str(indicator))

    if not search_result:
        print(f"Failed with indicator: {indicator}")
        raise FileNotFoundError("Project root not found!")
    else:
        return search_result


@lru_cache(maxsize=1)
def load_toml(toml_path: Path) -> dict:
    """Reads and caches a toml file"""
    if not toml_path.exists():
        raise FileNotFoundError(f"Invalid {toml_path=}")
    with open(toml_path, "rb") as file:
        return tomllib.load(file)


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


def pyproject_path() -> Path:
    """Path to own pyproject.toml file"""
    return find_project_root(indicator="pyproject.toml") / "pyproject.toml"


@lru_cache(maxsize=1)
def pyproject_toml() -> dict:
    """Read and cache pyproject.toml file as dict"""
    return load_toml(pyproject_path())


def pyproject_sns() -> SimpleNamespace:
    """Transform pyproject.toml into SimpleNamespace with dot acces"""
    toml: dict = pyproject_toml()
    return dict_to_sns(toml)


def pyproject_name() -> str:
    """Fetches project metadata from: [project] in pyproject.toml"""
    pyproject_file: SimpleNamespace = pyproject_sns()
    return pyproject_file.project.name  # WARNING: error not catched


def pyproject_log_section() -> SimpleNamespace:
    """Fetches from: [tool.silvasta.logging] in pyproject.toml"""
    pyproject: SimpleNamespace = pyproject_sns()
    tool_project_section: SimpleNamespace = getattr(
        pyproject.tool, pyproject_name()
    )
    return tool_project_section.logging


class PathGuard:
    """Centralized path enforcement toolkit"""

    @staticmethod
    def _ensure_dir_logic(path: Path) -> Path:
        """The actual implementation logic"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {path}")
        return path

    @overload
    @staticmethod
    def dir(target: Path) -> Path:
        """If you pass a Path, you get a Path back."""
        ...

    # INFO: overload used to get proper type checks at function calls

    @overload
    @staticmethod
    def dir(target: Callable[P, Path]) -> Callable[P, Path]:
        """If you pass a Callable, you get a Callable back with the exact same arguments."""
        ...

    @staticmethod
    def dir(
        target: Callable[P, Path] | Path,
    ) -> Callable[P, Path] | Path:
        """Hybrid: Ensure path is directory and exists, create if missing"""

        # Case 1: Used as a Function Call (PathGuard.dir(path))
        if isinstance(target, Path):
            return PathGuard._ensure_dir_logic(target)

        # Case 2: Used as a Decorator (@PathGuard.dir)
        if callable(target):

            @functools.wraps(target)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path: Path = target(
                    *args, **kwargs
                )  # The warning will now be gone!
                return PathGuard._ensure_dir_logic(path)

            return wrapper

        raise TypeError(
            f"Invalid target type for PathGuard.dir: {type(target)}"
        )

    @staticmethod
    def _ensure_file_logic(
        path: Path, raise_error=True, default_content: str | None = None
    ) -> Path:
        """The actual implementation logic"""
        path = Path(path)
        if not path.exists():
            logger.warning(f"File not found at: {path}")
            if default_content is not None:  # write first
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(default_content)
                logger.info(f"Created default file: {path}")
            if raise_error:
                raise FileNotFoundError(f"Critical file missing: {path}")
        return path

    # TASK: for later, check outsourcing type defs to .pyi file
    # - pro: centralized management, file here cleaner
    # - con: type hints here completele disabled
    # -> todo for entire file, more work, error prone

    @overload  # CASE 1: Decorator WITH Arguments (@PathGuard.file(default_content="..."))
    @staticmethod
    def file(
        target: None = None,
        *,  # forces keyword arguments, avoids passing f.e. string to `target`
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Callable[[Callable[P, Path]], Callable[P, Path]]: ...

    @overload  # CASE 2: Function Call -> PathGuard.file(path)
    @staticmethod
    def file(
        target: Path,
        raise_error: bool = True,
        default_content: str | None = None,
    ) -> Path: ...

    @overload  # CASE 3: Bare Decorator -> @PathGuard.file
    @staticmethod
    def file(target: Callable[P, Path]) -> Callable[P, Path]: ...

    @staticmethod
    def file(
        target: Callable[P, Path] | Path | None = None,
        raise_error=True,
        default_content: str | None = None,
    ) -> (
        Path
        | Callable[P, Path]
        | Callable[
            [Callable[P, Path]],
            Callable[P, Path],
        ]
    ):
        """Ensure path is file, write default content and | or raise error"""

        # CASE 1: Decorator WITH Arguments -> @PathGuard.file(default_content="...")
        if target is None:

            def decorator(func: Callable[P, Path]) -> Callable[P, Path]:
                @functools.wraps(func)
                def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                    path = Path(func(*args, **kwargs))
                    return PathGuard._ensure_file_logic(
                        path, raise_error, default_content
                    )

                return wrapper

            return decorator

        # CASE 2: Function Call -> PathGuard.file(path)
        if isinstance(target, Path):
            return PathGuard._ensure_file_logic(
                target, raise_error, default_content
            )

        # CASE 3: Bare Decorator -> @PathGuard.file
        if callable(target):

            @functools.wraps(target)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path = Path(target(*args, **kwargs))
                return PathGuard._ensure_file_logic(
                    path, raise_error, default_content
                )

            return wrapper

        raise TypeError(
            f"Invalid target type for PathGuard.file: {type(target)}"
        )

    @staticmethod
    def _get_unique_candidate(path: Path | str) -> Path:
        """Internal logic: Appends counter until a free filename is found."""

        path = Path(path)
        if not path.exists():
            return path

        counter = 1

        suffixes: str = "".join(path.suffixes)
        original_stem: str = (
            path.name[: -len(suffixes)] if suffixes else path.name
        )

        parent: Path = path.parent

        # Safety loop to find free slot
        while True:
            new_name = f"{original_stem}_{counter}{suffixes}"
            candidate: Path = parent / new_name
            if not candidate.exists():
                return candidate
            counter += 1

    @overload
    @staticmethod
    def unique(target: Path) -> Path:
        """If you pass a Path, you get a Path back."""
        ...

    @overload
    @staticmethod
    def unique(target: Callable[P, Path]) -> Callable[P, Path]:
        """If you pass a Callable, you get a Callable back with the exact same arguments."""
        ...

    @staticmethod
    def unique(
        target: Callable[P, Path] | Path,
    ) -> Callable[P, Path] | Path:
        """Hybrid: Ensures the returned path does NOT exist,
        If it exists, auto-increments suffix (file_1.txt, file_2.txt)"""

        # Case 1: Direct call (PathGuard.unique(path))
        if isinstance(target, Path):
            return PathGuard._get_unique_candidate(target)

        # Case 2: Bare Decorator (@PathGuard.unique)
        if callable(target):

            @functools.wraps(target)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path: Path = target(*args, **kwargs)
                return PathGuard._get_unique_candidate(path)

            return wrapper

        raise TypeError(
            f"Invalid target type for PathGuard.unique: {type(target)}"
        )

    @staticmethod
    def find_sequence(base_target: Path) -> list[Path]:
        """Find all paths of a sequence (base name + auto-incremented versions)
        returns list, sorted by modification time (newest first)"""

        base = Path(base_target)
        parent = base.parent
        if not parent.exists():
            return []

        # Same logic as in _get_unique_candidate
        suffixes: str = "".join(base.suffixes)
        original_stem: str = (
            base.name[: -len(suffixes)] if suffixes else base.name
        )

        #  re.escape to ensure special chars  don't break regex
        suffix_esc: str = re.escape(suffixes)
        stem_esc: str = re.escape(original_stem)

        # regex matches "stem.suffix" OR "stem_digits.suffix"
        pattern: re.Pattern[str] = re.compile(
            rf"^{stem_esc}(_\d+)?{suffix_esc}$"
        )

        sequence: list[Path] = [
            item for item in parent.iterdir() if pattern.match(item.name)
        ]
        sequence.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        return sequence

    @staticmethod
    def prune(base_target: Path, remaining: int = 5) -> list[Path]:
        """Remove oldest files/dirs from sequence (name_NUM{.*}) until remaining"""

        candidates = PathGuard.find_sequence(base_target)

        if len(candidates) <= remaining:
            return []

        to_delete = candidates[remaining:]
        deleted_paths = []

        for path in to_delete:
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                    logger.info(f"Pruned old dir: {path.name}")
                else:
                    path.unlink()
                    logger.info(f"Pruned old file: {path.name}")
                deleted_paths.append(path)
            except OSError as e:
                logger.error(f"Failed to prune {path}: {e}")

        return deleted_paths

    @staticmethod
    def rotate(
        source: Path | str, target: Path | str, reset: bool = False
    ) -> Path:
        """Moves source (file or dir) to target, handles unique naming collisions,
        if reset=True, recreates empty file or directory at original 'source' location"""
        source = Path(source)
        target = Path(target)

        if not source.exists():
            raise FileNotFoundError(f"Cannot rotate missing path: {source}")

        # Store type for reset logic later
        is_directory = source.is_dir()

        PathGuard._ensure_dir_logic(target.parent)
        final_target: Path = PathGuard.unique(target)

        shutil.move(str(source), str(final_target))

        try:  # use relative path for log, if possible
            log_src = source.resolve().relative_to(Path.cwd())
            log_dst = final_target.resolve().relative_to(Path.cwd())
        except ValueError:
            log_src = source.name
            log_dst = final_target.name
        logger.debug(f"Rotated: {log_src} -> {log_dst}")

        if reset:
            if is_directory:
                source.mkdir()
                logger.debug(f"Recreated empty directory: {source}")
            else:
                source.touch()
                logger.debug(f"Reset empty file: {source}")

        return final_target
