import functools
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, cast

from loguru import logger

P = ParamSpec("P")


class PathGuard:
    """Centralized path enforcement toolkit"""

    @staticmethod
    def _ensure_input(
        path: Path | str,
        resolve: bool = False,
        check_exists: bool = False,
        must_exists: bool = False,
    ) -> Path:
        """Confirm path is Path, attach other checks if needed"""
        path = Path(path)

        if resolve:
            path: Path = path.resolve()

        if check_exists or must_exists:
            text: str = "exists!" if path.exists() else "not found on disk!"
            msg = f"input {text} for: {path=}"

        if check_exists:
            logger.info(msg)

        if must_exists:
            if not path.exists():
                raise FileNotFoundError(msg)
            if not check_exists:
                logger.debug(msg)

        return path

    @staticmethod
    def _ensure_dir_logic(path: Path | str) -> Path:
        """The actual implementation logic"""
        path: Path = PathGuard._ensure_input(path)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"directory ensured: {path}")
        return path

    @staticmethod
    def dir(
        target: Callable[P, Path] | Path | str,
    ) -> Callable[P, Path] | Path:
        """Hybrid: Ensure path is directory and exists, create if missing"""

        # Case 1: Used as a Function Call (PathGuard.dir(path))
        if isinstance(target, (Path, str)):
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
        path: Path | str, raise_error: bool, default_content: str | None
    ) -> Path:
        """The actual implementation logic"""

        path: Path = PathGuard._ensure_input(path)

        if path.exists():
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
                warn = "Suppress error only allowed for case of writing file with default content!"
                logger.warning(warn)
                msg = f"Wrong input, can't confirm:\n{path}"

        raise FileNotFoundError(msg)

    @staticmethod
    def file(
        target: Callable[P, Path] | Path | str | None = None,
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

        # CASE 1: Function Call -> PathGuard.file(path)
        if isinstance(target, (Path, str)):
            return PathGuard._ensure_file_logic(
                target, raise_error, default_content
            )

        # CASE 2: Bare Decorator -> @PathGuard.file
        if callable(target):
            func = cast(Callable[P, Path], target)

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path = Path(func(*args, **kwargs))
                return PathGuard._ensure_file_logic(
                    path, raise_error, default_content
                )

            return wrapper

        # CASE 3: Decorator with Arguments -> @PathGuard.file(default_content="...")
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

        raise TypeError(
            f"Invalid target type for PathGuard.file: {type(target)}"
        )

    @staticmethod
    def _get_unique_candidate(path: Path | str, ensure_parent: bool) -> Path:
        """Internal logic: Appends counter until a free filename is found."""

        path: Path = PathGuard._ensure_input(path)

        if not path.exists():  # TEST: check how much this spams
            msg = "path already unique, "
            if path.parent.exists():
                logger.debug(msg + "path has parent")
            else:
                msg += "path has no parent, "
                if ensure_parent:
                    PathGuard._ensure_dir_logic(path.parent)
                    logger.info(msg + "parent ensured!")
                else:
                    logger.warning(f"{msg} take care before write! {path=}")

            return path

        # prevent f.e. my_archive.tar_1.gz
        suffixes: str = "".join(path.suffixes)
        original_stem: str = (
            path.name[: -len(suffixes)] if suffixes else path.name
        )

        parent: Path = path.parent
        counter = 1

        while True:  # Safety loop to find free slot
            new_name = f"{original_stem}_{counter}{suffixes}"
            candidate: Path = parent / new_name
            if not candidate.exists():
                logger.info(f"New unique path: {candidate}")
                break
            counter += 1

        logger.info(f"Incremented path by {counter}: {candidate}")

        return candidate

    @staticmethod
    def unique(
        target: Callable[P, Path] | Path | str | None = None,
        ensure_parent=False,
    ) -> (
        Path
        | Callable[P, Path]
        | Callable[
            [Callable[P, Path]],
            Callable[P, Path],
        ]
    ):
        """Hybrid: Ensures the returned path does NOT exist,
        ensure_parent creates folder to make it directly writable.
        If it exists, auto-increments suffix (file_1.txt, file_2.txt)
        """

        # Case 1: Direct call (PathGuard.unique(path))
        if isinstance(target, (Path, str)):
            return PathGuard._get_unique_candidate(target, ensure_parent)

        # Case 2: Bare Decorator (@PathGuard.unique)
        if callable(target):
            func = cast(Callable[P, Path], target)

            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                path: Path = Path(func(*args, **kwargs))
                return PathGuard._get_unique_candidate(path, ensure_parent)

            return wrapper

        # CASE 3: Decorator with args -> @PathGuard.unique(ensure_parent=True)
        if target is None:

            def decorator(func: Callable[P, Path]) -> Callable[P, Path]:
                @functools.wraps(func)
                def wrapper(*args: P.args, **kwargs: P.kwargs) -> Path:
                    path: Path = Path(func(*args, **kwargs))
                    return PathGuard._get_unique_candidate(path, ensure_parent)

                return wrapper

            return decorator
        raise TypeError(
            f"Invalid target type for PathGuard.unique: {type(target)}"
        )

    @staticmethod
    def find_sequence(base_target: Path | str) -> list[Path]:
        """Find all paths of a sequence (base name + auto-incremented versions)
        returns list, sorted by modification time (newest first)"""

        base: Path = PathGuard._ensure_input(base_target)

        if not (parent := base.parent).exists():
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
    def prune(base_target: Path | str, remaining: int = 5) -> list[Path]:
        """Remove oldest files/dirs from sequence (name_NUM{.*}) until remaining"""

        candidates: list[Path] = PathGuard.find_sequence(base_target)

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

        source: Path = PathGuard._ensure_input(source, must_exists=True)
        target: Path = PathGuard._ensure_input(target)

        # Store type for reset logic later
        is_directory: bool = source.is_dir()

        final_target: Path = PathGuard._get_unique_candidate(
            target, ensure_parent=True
        )

        shutil.move(str(source), str(final_target))

        log_src: str = PathGuard.get_relative_or_name(source)
        log_dst: str = PathGuard.get_relative_or_name(target)

        logger.debug(f"Rotated: {log_src} -> {log_dst}")

        if reset:
            if is_directory:
                source.mkdir()
                logger.debug(f"Recreated empty directory: {source}")
            else:
                source.touch()
                logger.debug(f"Reset empty file: {source}")

        return final_target

    @staticmethod
    def get_relative_or_name(
        target: Path | str,
        root: Path | str | None = None,
        check_exists: bool = False,
        must_exists: bool = False,
    ) -> str:
        """Get relative path string to root|CWD if exists or path.name"""
        path: Path = PathGuard._ensure_input(
            path=target,
            check_exists=check_exists,
            must_exists=must_exists,
        )
        try:
            return str(PathGuard.relative(path, root))
        except ValueError:
            return Path(target).name

    @staticmethod
    def relative(
        target: Path | str,
        root: Path | str | None = None,
        strict: bool = True,
        check_exists: bool = False,
        must_exists: bool = False,
    ) -> Path:
        """Find relative path starting at root|CWD downwards to target"""

        target_path: Path = PathGuard._ensure_input(
            path=target,
            resolve=True,
            check_exists=check_exists,
            must_exists=must_exists,
        )
        root_path: Path = PathGuard._ensure_input(
            path=root or Path.cwd(),
            resolve=True,
            check_exists=check_exists,
            must_exists=must_exists,
        )
        if strict:
            try:
                return target_path.relative_to(root_path)
            except ValueError as e:
                msg = f"{target_path=} not found in {root_path=}"
                raise ValueError(msg) from e
        else:
            import os

            return Path(os.path.relpath(target_path, root_path))

    @staticmethod
    def relative_duo(
        path1: Path | str,
        path2: Path | str,
        check_exists: bool = False,
        must_exists: bool = False,
    ) -> Path | None:
        """Find relative path from any of both directions or get None"""

        path1: Path = PathGuard._ensure_input(
            path=path1,
            check_exists=check_exists,
            must_exists=must_exists,
        )
        path2: Path = PathGuard._ensure_input(
            path=path2,
            check_exists=check_exists,
            must_exists=must_exists,
        )
        try:
            rel21 = PathGuard.relative(path1, path2, strict=True)
        except ValueError:
            rel21 = None

        try:
            rel12 = PathGuard.relative(path2, path1, strict=True)
        except ValueError:
            rel12 = None

        match (rel21, rel12):
            case (None, None):
                logger.info("No relative path found in both directions...")
                return None

            case (Path() as p, None) | (None, Path() as p):
                logger.debug(f"found relative path: {p}")
                return p

            case _:
                logger.info("It happened, how is that possible?")
                logger.error(f"Found: {rel21} and {rel12}?")
                return None

    @functools.singledispatch
    @staticmethod
    def split_read_print_path(target, local_root: Path | None = None):
        raise NotImplementedError(
            f"unsupported: {type(target)=}, path(s): {target=} and {local_root=}"
        )

    @split_read_print_path.register
    @staticmethod
    def _(
        target: list, local_root: Path | None = None
    ) -> list[tuple[Path, Path]]:
        return [
            PathGuard.split_read_print_path(path, local_root)
            for path in target
        ]

    @split_read_print_path.register
    @staticmethod
    def _(target: Path, local_root: Path | None = None) -> tuple[Path, Path]:

        if target.is_absolute():
            read_path: Path = target
            print_path: Path = (
                target
                if local_root is None
                else PathGuard.relative(target, local_root)
            )
        else:  # Relative target
            if local_root is None:
                raise ValueError(
                    f"Can't construct proper Path with {local_root=} for: {target=}"
                )
            read_path: Path = local_root / target
            print_path: Path = target
        return read_path, print_path
