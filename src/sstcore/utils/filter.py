import functools
from dataclasses import dataclass, field
from functools import singledispatchmethod
from pathlib import Path

from loguru import logger


def debug_log(func):
    """Decorator that logs target_set and corresponding class attribute"""

    @functools.wraps(func)
    def wrapper(self, target_set, *args, **kwargs):
        if self._debug:
            attr_name: str = func.__name__.replace("fulfills_", "")
            attr_value: set | None = getattr(self, attr_name, None)
            logger.debug(f"{attr_name}={attr_value}, {target_set=}")
        return func(self, target_set, *args, **kwargs)

    return wrapper


@dataclass
class FilterSet[SetType: str | Path | int, ObjectType]:
    """Create set that takes input(s) and answers if they match the loaded criteria"""

    exclude: set[SetType] = field(default_factory=set)
    require_all: set[SetType] = field(default_factory=set)
    require_any: set[SetType] = field(default_factory=set)

    allow_hidden_files: bool = False

    # Get complementary negative set, instead get all matching, get all others
    return_if_not_hit: bool = False

    _debug: bool = False

    @singledispatchmethod
    def __call__(self, target):
        raise NotImplementedError(f"Cannot process {type(target)=}")

    @__call__.register
    def _(self, target: str | Path | int) -> bool:
        """String input -> returns filename string"""
        target_set: set[SetType] = self._create_target_set(target)
        return self.fulfills_all_conditions(target_set)

    @__call__.register
    def _(self, target: list) -> list[ObjectType]:
        """String input -> returns filename string"""
        filtered: list[ObjectType] = []

        for item in target:
            target_set: set[SetType] = self._create_target_set(item)
            hit: bool = self.fulfills_all_conditions(target_set)

            # Attach 'hit' or 'not hit = missing' depending if flag is active
            if hit != self.return_if_not_hit:
                filtered.append(item)

        return filtered

    @singledispatchmethod
    def _create_target_set(self, target: ObjectType) -> set[SetType]:
        """Override this for specific object handling!"""

        raise NotImplementedError(f"Cannot process {type(target)=}")

    @_create_target_set.register
    def _(self, target: str | Path | int) -> set:
        return {target}

    @debug_log
    def fulfills_exclude(self, target_set: set[SetType]) -> bool:
        """Condition 1: Must NOT have any excluded keywords"""
        if self.exclude:
            # Must NOT have any excluded keywords
            if not self.exclude.isdisjoint(target_set):
                return False

        return True

    @debug_log
    def fulfills_require_all(self, target_set: set[SetType]) -> bool:
        """Condition 2: Must have ALL required keywords"""
        if self.require_all:
            # Must have ALL required keywords
            if not self.require_all.issubset(target_set):
                return False

        return True

    @debug_log
    def fulfills_require_any(self, target_set: set[SetType]) -> bool:
        """Condition 3: Must have AT LEAST ONE required_any keyword"""
        if self.require_any:
            # Must have AT LEAST ONE required_any keyword
            if self.require_any.isdisjoint(target_set):
                return False

        return True

    def fulfills_all_conditions(self, target_set: set[SetType]) -> bool:
        """Compare internal registry with target keyword set"""

        if not self.fulfills_exclude(target_set):
            return False

        if not self.fulfills_require_all(target_set):
            return False

        if not self.fulfills_require_any(target_set):
            return False

        return True


@dataclass
class PathFilter(FilterSet):
    def _create_target_set(self, target: Path) -> set[str]:
        return set(target.parts) | {target.stem} | {target.suffix}


PROJECT_IGNORE_DIRS: set[str] = {
    # MOVE: to config.defaults or new class
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "target",
}

PROJECT_ALLOWED_EXTS: set[str] = {
    # MOVE: to config.defaults or new class
    ".py",
    ".rs",
    ".md",
    ".json",
    ".yaml",
    ".toml",
}


@dataclass
class ProjectFilter(PathFilter):
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
