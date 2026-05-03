import functools
import re
from abc import abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, cast, Any

from loguru import logger

from sstcore.exceptions import NotImplementedDispachError

P = ParamSpec("P")


class _TemporaryPythonVersionDispacher:
    """Intended to group commands by Python 3.14 or smaller"""

    @staticmethod
    def move(source: Path, target: Path):
        raise NotImplementedError

    @staticmethod
    def copy(source: Path, target: Path):
        raise NotImplementedError


_fs_operator: _TemporaryPythonVersionDispacher | None = None


def _get_fs_operator() -> _TemporaryPythonVersionDispacher:

    global _fs_operator
    if _fs_operator is None:
        import sys

        _fs_operator = _load_fs_operator(sys.version_info)

    return _fs_operator


def _load_fs_operator(version: tuple) -> _TemporaryPythonVersionDispacher:

    if version < (3, 14, 0):
        import shutil

        class _PythonOld(_TemporaryPythonVersionDispacher):
            @abstractmethod
            @staticmethod
            def move(source: Path, target: Path):
                shutil.move(source, target)

            @abstractmethod
            @staticmethod
            def copy(source: Path, target: Path):
                shutil.copy(source, target)

        return _PythonOld()
    else:

        class _Python314plus(_TemporaryPythonVersionDispacher):
            @abstractmethod
            @staticmethod
            def move(source: Path, target: Path):
                source.move(target)  # ty:ignore

            @abstractmethod
            @staticmethod
            def copy(source: Path, target: Path):
                source.copy(target)  # ty:ignore

        return _Python314plus()


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

        # Same logic as in find_sequence, consider when adapt!
        suffixes: str = "".join(path.suffixes)
        original_stem: str = (  # prevent f.e. my_archive.tar_1.gz
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

    @staticmethod
    def find_sequence(base_target: Path | str) -> list[Path]:
        """Find all paths of a sequence (base name + auto-incremented versions)
        returns list, sorted by modification time (newest first)"""

        base: Path = PathGuard._ensure_input(base_target)

        if not (parent := base.parent).exists():
            return []

        # Same logic as in _get_unique_candidate, consider when adapt!
        suffixes: str = "".join(base.suffixes)
        original_stem: str = (  # TODO: what if stem has already _NUM ?
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
        # LATER: make sort strategy or flag, check as well how to use in PathGuard.prune
        sequence.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        return sequence

    @staticmethod
    def prune(
        base_target: Path | str, remaining: int = 5, trash=False
    ) -> list[Path]:
        """Remove oldest files/dirs from sequence (name_NUM{.*}) until remaining"""

        if remaining >= len(sequence := PathGuard.find_sequence(base_target)):
            return []

        paths_to_delete: list[Path] = sequence[remaining:]

        _prune: Callable[[Path], bool] = (
            PathGuard.trash if trash else PathGuard.remove
        )
        return [path for path in paths_to_delete if _prune(path)]

    @staticmethod
    def remove(target: Path | str) -> bool:
        """Remove file or folder at target location"""

        def _remove(path: Path):
            if path.is_dir():
                import shutil  # LATER: upgrade with pathlib?

                shutil.rmtree(path)
            else:
                path.unlink()

        return PathGuard._clear_file_or_folder(target, clear_strategy=_remove)

    @staticmethod
    def trash(target: Path | str) -> bool:
        """Move file or folder at target location to system trash"""

        def _trash(path: Path):
            from send2trash import send2trash

            send2trash(path)

        return PathGuard._clear_file_or_folder(target, clear_strategy=_trash)

    @staticmethod
    def _clear_file_or_folder(
        target: Path | str, clear_strategy: Callable[[Path], Any]
    ) -> bool:
        """Handle args, logs and errors for deleting files or folders"""
        _clear: str = getattr(clear_strategy, "__name__", "_clear")
        clear: str = _clear.strip("_").capitalize()
        try:
            target: Path = PathGuard._ensure_input(target, must_exists=True)
            clear_strategy(target)
            logger.success(f"{clear}: {target}")
            return True

        except FileNotFoundError:
            logger.error(f"Nothing to {clear}: missing {target=}")
        except OSError as e:
            logger.error(f"OSError for {clear}: {target=}\n{e}")
        return False

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

        unique_target: Path = PathGuard._get_unique_candidate(
            target, ensure_parent=True
        )
        _get_fs_operator().move(source, unique_target)
        logger.debug(
            f"Rotated: {PathGuard.relative_string(source, unique_target)}"
        )

        if reset:
            if is_directory:
                source.mkdir()
                logger.debug(f"Recreated empty directory: {source}")
            else:
                source.touch()
                logger.debug(f"Reset empty file: {source}")

        return unique_target

    @staticmethod
    def copy(source: Path | str, target: Path | str) -> Path:
        """Copy source (file or dir) to target, handles unique naming collisions"""

        source: Path = PathGuard._ensure_input(source, must_exists=True)
        target: Path = PathGuard._ensure_input(target)

        unique_target: Path = PathGuard._get_unique_candidate(
            target, ensure_parent=True
        )
        _get_fs_operator().copy(source, unique_target)

        logger.debug(
            f"Copied: {PathGuard.relative_string(source, unique_target)}"
        )
        return unique_target

    @staticmethod
    def hardlink(source: Path | str, target: Path | str) -> Path:
        """Create a hardlink of source to target, handles unique naming collisions"""

        source: Path = PathGuard._ensure_input(source, must_exists=True)
        target: Path = PathGuard._ensure_input(target)

        unique_target: Path = PathGuard._get_unique_candidate(
            target, ensure_parent=True
        )

        try:
            unique_target.hardlink_to(source)
            logger.debug(
                f"Hardlinked: {PathGuard.relative_string(source, unique_target)}"
            )
        except OSError as e:
            logger.error("Hardlink failed! Source and Target on same drive?")
            logger.error(f"{source=}, {target=}")
            raise e

        return unique_target

    @staticmethod
    def symlink(source: Path | str, target: Path | str) -> Path:
        """Create absolute symlink of source to target, handles unique naming collisions"""

        # Important: Resolve source to absolute path, link breaks otherwise
        source: Path = PathGuard._ensure_input(
            source, must_exists=True, resolve=True
        )
        target: Path = PathGuard._ensure_input(target)

        unique_target: Path = PathGuard._get_unique_candidate(
            target, ensure_parent=True
        )

        unique_target.symlink_to(source)
        logger.debug(
            f"Symlinked: {PathGuard.relative_string(source, unique_target)}"
        )
        return unique_target

    @staticmethod
    def relative_string(source: Path, target: Path):
        relative: Path | None = PathGuard.relative_duo(source, target)
        relative: Path = relative or PathGuard.relative(
            target=target, root=source, strict=False
        )
        return f"{source.name} -> {relative}"

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
        raise NotImplementedDispachError(target, local_root)

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
