import functools
import logging
import os
import re
import shutil
import tomllib
from enum import Enum, auto
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, ParamSpec, Union, overload

logger: logging.Logger = logging.getLogger(__name__)

P = ParamSpec("P")

# WARNING: path.pyi is not active, check if confusion with type hints  occurs!


class XDG_HOMES(Enum):
    DATA = auto()
    STATE = auto()
    CONFIG = auto()

    @property
    def path(self) -> Path:
        env_var_key = f"XDG_{self.name}_HOME"
        return Path(os.getenv(env_var_key, self._default_path()))

    def _default_path(self) -> Path:
        mapping: dict = {
            XDG_HOMES.DATA: ".local/share",
            XDG_HOMES.STATE: ".local/state",
            XDG_HOMES.CONFIG: ".config",
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
    tool_project_section: SimpleNamespace = getattr(pyproject.tool, pyproject_name())
    return tool_project_section.logging


class PathGuard:
    """Centralized path enforcement toolkit"""

    @overload
    @staticmethod
    def dir(target: Path) -> Path:
        """If you pass a Path, you get a Path back."""
        ...

    # NOTE: overload needed to get proper type checks at function calls

    @overload
    @staticmethod
    def dir(target: Callable[P, Path]) -> Callable[P, Path]:
        """If you pass a Callable, you get a Callable back with the exact same arguments."""
        ...

    @staticmethod
    def dir(target: Union[Callable[P, Path], Path]) -> Union[Callable[P, Path], Path]:
        """Hybrid: Ensure path is directory and exists, create if missing"""

        # Case 1: Used as a Function Call (PathGuard.dir(path))
        if isinstance(target, Path):
            return PathGuard._ensure_dir_logic(target)

        # Case 2: Used as a Decorator (@PathGuard.dir)
        @functools.wraps(target)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
            path: Path = target(*args, **kwargs)  # The warning will now be gone!
            return PathGuard._ensure_dir_logic(path)

        return wrapper

    @staticmethod
    def _ensure_dir_logic(path: Path) -> Path:
        """The actual implementation logic"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {path}")
        return path

    @overload
    @staticmethod
    def file(target: Path) -> Path:
        """If you pass a Path, you get a Path back."""
        ...

    # TASK: for later, outsource type defs to .pyi file

    @overload
    @staticmethod
    def file(target: Callable[P, Path]) -> Callable[P, Path]:
        """If you pass a Callable, you get a Callable back with the exact same arguments."""
        ...

    @staticmethod
    def file(
        target: Union[Callable[P, Path], Path],
        raise_error=True,
        default_content: str | None = None,
    ) -> Union[Callable[P, Path], Path]:
        """Ensure path is file, write default content and | or raise error"""

        # Case 1: Used as a Function Call (PathGuard.file(path))
        if isinstance(target, Path):
            return PathGuard._ensure_file_logic(target, raise_error, default_content)

        # Case 2: Used as a bare Decorator (@PathGuard.file)
        @functools.wraps(target)
        def wrapper(*args, **kwargs) -> Path:
            path = Path(target(*args, **kwargs))
            return PathGuard._ensure_file_logic(path, raise_error, default_content)

        return wrapper

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

    @overload
    @staticmethod
    def unique(target: Path) -> Path:
        """If you pass a Path, you get a Path back."""
        ...

    # TASK: for later, outsource type defs to .pyi file

    @overload
    @staticmethod
    def unique(target: Callable[P, Path]) -> Callable[P, Path]:
        """If you pass a Callable, you get a Callable back with the exact same arguments."""
        ...

    @staticmethod
    def unique(
        target: Union[Callable[P, Path], Path],
    ) -> Union[Callable[P, Path], Path]:
        """Hybrid: Ensures the returned path does NOT exist,
        If it exists, auto-increments suffix (file_1.txt, file_2.txt)"""

        if isinstance(target, Path):
            # Case 1: Direct call (PathGuard.unique(path))
            return PathGuard._get_unique_candidate(target)

        # AI: this was the second fix, looks solid?

        # Case 2: Used as Decorator (@PathGuard.unique)
        @functools.wraps(target)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
            path: Path = target(*args, **kwargs)
            return PathGuard._get_unique_candidate(path)

        return wrapper

    @staticmethod
    def _get_unique_candidate(path: Path) -> Path:
        """Internal logic: Appends counter until a free filename is found."""
        path = Path(path)
        if not path.exists():
            return path

        counter = 1
        original_stem = path.stem
        suffix = path.suffix
        parent = path.parent

        # Safety loop to find free slot
        while True:
            new_name = f"{original_stem}_{counter}{suffix}"
            candidate = parent / new_name
            if not candidate.exists():
                return candidate
            counter += 1

    @staticmethod
    def find_sequence(base_target: Path) -> list[Path]:
        """Find all paths of a sequence (base name + auto-incremented versions)
        returns list, sorted by modification time (newest first)"""

        base = Path(base_target)
        parent = base.parent
        if not parent.exists():
            return []

        stem_esc: str = re.escape(base.stem)
        #  re.escape to ensure special chars  don't break regex
        suffix_esc: str = re.escape(base.suffix)
        # regex matches "stem.suffix" OR "stem_digits.suffix"
        pattern: re.Pattern[str] = re.compile(rf"^{stem_esc}(_\d+)?{suffix_esc}$")

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
    def rotate(source: Path, target: Path, reset: bool = False) -> Path:
        """Moves source (file or dir) to target, handles unique naming collisions,
        if reset=True, recreates empty file or directory at original 'source' location"""
        source = Path(source)
        target = Path(target)

        if not source.exists():
            raise FileNotFoundError(f"Cannot rotate missing path: {source}")

        # Store type for reset logic later
        is_directory = source.is_dir()
        # Ensure destination parent exists
        PathGuard._ensure_dir_logic(target.parent)

        final_target: Path = PathGuard.unique(target)

        shutil.move(str(source), str(final_target))

        try:
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
