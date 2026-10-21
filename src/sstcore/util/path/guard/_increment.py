"""
Incremental Sequence

.
"""

import re

__all__: list[str] = [
    "unique_candidate",
    "iter_unique_candidates",
    "split_stem_suffixes",
    "find_sequence",
]

import itertools
from collections.abc import Iterator
from pathlib import Path

from loguru import logger

from ._arg import TargetPath, castpath


@castpath
def unique_candidate(path: TargetPath, ensure_parent: bool) -> Path:
    """PathGuard.unique implementation logic: Increment until Path is unique"""

    if not path.exists():
        _document_unique_path(path, ensure_parent)
        return path

    for candidate in iter_unique_candidates(path, include_base=True):
        if not candidate.exists():
            if candidate != path:
                logger.info(f"Incremented: {candidate.name}")
            return candidate

    raise RuntimeError("Unreachable: infinite generator finished")


def iter_unique_candidates(
    base: Path, /, *, include_base: bool = True
) -> Iterator[Path]:
    """Yield candidate Paths in sequence: stem_1.ext - stem_2.ext"""

    if include_base:
        yield base

    stem, suffixes = split_stem_suffixes(base)
    parent: Path = base.parent

    for counter in itertools.count(1):
        yield parent / _unique_pattern(stem, counter, suffixes)


def split_stem_suffixes(path: Path, /, *, escape=False) -> tuple[str, str]:
    """Prevent stuff like: my_archive.tar_1.gz"""
    suffixes: str = "".join(path.suffixes)
    stem: str = path.name[: -len(suffixes)] if suffixes else path.name
    if escape:
        return re.escape(pattern=stem), re.escape(pattern=suffixes)
    return stem, suffixes


def _unique_pattern(stem: str, counter: int, suffixes: str) -> str:
    # TODO: connect with brick.parse.name
    """The Incremental Schema"""
    return f"{stem}_{counter}{suffixes}"


def _document_unique_path(path: Path, ensure_parent: bool):
    if not path.parent.exists():
        if ensure_parent:
            path.mkdir(parents=True, exist_ok=True)  # REMOVE:
            logger.debug("path already unique, parent ensured!")
        else:
            logger.info(f"Path unique but without directory! {path=}")


@castpath
def find_sequence(base: TargetPath) -> list[Path]:
    """
    Find all Paths of a Sequence (base name + auto-incremented versions)

    Return list sorted by modification time (newest first)
    """

    if not (parent := base.parent).exists():
        return []

    stem, suffixes = split_stem_suffixes(base, escape=True)
    pattern = rf"^{stem}(_\d+)?{suffixes}$"

    # NOTE: needed? compile for 1 usage?
    compiled: re.Pattern[str] = re.compile(pattern)

    sequence: list[Path] = [
        item
        for item in parent.iterdir()  #
        if compiled.match(item.name)
    ]

    # LATER: check if and how to isolate this
    sequence.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return sequence
