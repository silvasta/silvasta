import functools
import logging
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, cast

logger = logging.getLogger(__name__)  # LATER: logs usage in other projects

P = ParamSpec("P")


class PathGuard:
    """Centralized path enforcement toolkit"""

    @staticmethod
    def _ensure_dir_logic(path: Path) -> Path:
        """The actual implementation logic"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ensured: {path}")
        return path

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
            func = cast(Callable[P, Path], target)

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path: Path = func(*args, **kwargs)
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

        if (path := Path(path)).exists():  # just to be 100% sure
            return path

        logger.warning(f"File not found at: {path}")

        if default_content is not None:  # write first
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(default_content)
            logger.info(f"Created default file:\n{path}")

            if raise_error:
                msg = f"Critical file created, modify at:\n{path}"
            else:
                return path
        else:
            if raise_error:
                msg = f"Critical file missing: {path}"
            else:
                warn = "Surpress error only allowed for case of writing file with default content!"
                logger.warning(warn)
                msg = f"Wrong input, can't confirm:\n{path}"

        raise FileNotFoundError(msg)

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
            func = cast(Callable[P, Path], target)

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path = Path(func(*args, **kwargs))
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

        # WARNING: can return path for f.e. plot that is unique but not writable
        # - main issue is that the parent of the new file not exists
        # - always create parent here? most likely not, but as arg? or single PathGuard method? (that stacks others)

        if not (path := Path(path)).exists():  # just to be 100% sure
            return path

        # prevent f.e. my_archive.tar_1.gz
        suffixes: str = "".join(path.suffixes)
        original_stem: str = (
            path.name[: -len(suffixes)] if suffixes else path.name
        )

        parent: Path = path.parent
        counter = 1

        # Safety loop to find free slot
        while True:
            new_name = f"{original_stem}_{counter}{suffixes}"
            candidate: Path = parent / new_name
            if not candidate.exists():
                logger.info(f"New unique path: {candidate}")
                return candidate
            counter += 1

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
            func = cast(Callable[P, Path], target)

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path: Path = Path(func(*args, **kwargs))
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
        final_target: Path = PathGuard._get_unique_candidate(target)

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
