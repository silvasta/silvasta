from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger
from pydantic import ValidationError

from ..parse import ParsedName
from .set import FilterSet


@dataclass
class PathFilter(FilterSet[str, Path]):
    """Modified Target Set that decomposes Paths."""

    def _create_target_set(self, target: Path) -> set[str]:
        return set(target.parts) | {target.stem} | {target.suffix}


PROJECT_IGNORE_DIRS: set[str] = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "target",
}

PROJECT_ALLOWED_EXTS: set[str] = {
    ".py",
    ".pyi",
    ".rs",
    ".md",
    ".json",
    ".yaml",
    ".toml",
    ".tex",
    ".cls",
}


@dataclass
class ProjectFilter(PathFilter):
    """Setup with defaults for files of Coding Projects."""

    exclude: set[str] = field(
        default_factory=lambda: set(PROJECT_IGNORE_DIRS),
    )
    require_any: set[str] = field(
        default_factory=lambda: set(PROJECT_ALLOWED_EXTS)
    )

    def __call__(self, target: Path) -> bool:
        target_set: set[str] = self._create_target_set(target)

        if not self.allow_hidden_files and target.name.startswith("."):
            return False

        if target.is_dir():
            return self.fulfills_exclude(target_set)

        if target.is_file():
            return self.fulfills_require_any(target_set)

        raise ValueError(f"Invalid path, got {target=}")


@dataclass(kw_only=True)
class PatternFilter(PathFilter):
    """Filter by parsing filenames with ParsedName regex matcher!"""

    # INFO: newly added Derivative, not used or tested so far!

    parser: ParsedName

    exclude: set[str] = field(default_factory=lambda: set(PROJECT_IGNORE_DIRS))

    def __call__(self, target: Path) -> bool:
        """Evaluate if the path should be yielded or traversed."""

        # 1. Ignore hidden files/folders (unless overridden)
        if not self.allow_hidden_files and target.name.startswith("."):
            return False

        # 2. Directories: Rely on standard set-exclusion to prune the walk tree
        if target.is_dir():
            target_set: set[str] = self._create_target_set(target)
            # NEXT: test and adapt
            # WARN: this needs to match directories as well sometimes!!
            return self.fulfills_exclude(target_set)

        # 3. Files: Attempt to parse the filename
        if target.is_file():
            try:
                self.parser(target)  # match if succeeded!
                return True

            except (ValueError, ValidationError) as e:
                # ValueError: Regex pattern didn't match
                # ValidationError: Matched, but schema types failed
                if self._debug:
                    logger.debug(
                        f"ignoring file {target.name=}, parse failed: {e}"
                    )
                return False

        return False
