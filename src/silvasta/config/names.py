import re
from functools import singledispatchmethod
from pathlib import Path
from typing import Annotated, Any, Self

from loguru import logger
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PrivateAttr,
    model_validator,
)
from pydantic_settings import BaseSettings

from silvasta.utils.parse import PatternNamer


class ParsedName(BaseModel):
    pattern: str
    keys: list[str] = Field(default_factory=list)

    _namer: PatternNamer = PrivateAttr()

    @property
    def n_keys(self) -> int:
        return len(self.keys)

    @model_validator(mode="after")
    def _sync_namer_and_keys(self) -> Self:
        """Runs automatically whenever the model is instantiated or updated."""
        self._namer = PatternNamer(self.pattern)

        if self.keys and set(self.keys) != set(self._namer.keys):
            logger.error(
                f"Configured pattern '{self.pattern}' changed expected keys! "
                f"Expected: {self.keys}, Found: {self._namer.keys}. "
                f"Paths generated with this pattern might contain 'UNKNOWN' placeholders."
            )

        # Sync to the actual keys requested by the pattern
        self.keys: list[str] = self._namer.keys

        return self

    @singledispatchmethod
    def __call__(self, target):
        raise NotImplementedError(f"Cannot process {type(target)=}, {target=}")

    @__call__.register
    def _(self, target: dict) -> str:
        """Forwards parsing key value pairs to name"""

        # Ensure every key required by the pattern exists in the target dict
        safe_target: dict[str, str] = {}

        for key in self.keys:
            if key not in target:
                logger.error(
                    f"Missing key '{key}' for pattern '{self.pattern}'. Using fallback."
                )
                safe_target[key] = f"UNKNOWN_{key.upper()}"
            else:
                safe_target[key] = target[key]

        return self._namer.format(**safe_target)

    @__call__.register
    def _(self, target: list) -> str:
        """Forwards parsing key value pairs to name"""

        # Ensure every key required by the pattern exists in the target dict
        safe_target: dict[str, str] = {}
        n_values: int = len(target)

        for i, key in enumerate(self.keys):
            if i < n_values:
                safe_target[key] = target[i]

            # Error Case 1: less values provided than keys
            if i >= n_values:
                msg: str = f"Missing value for {key=}! Using fallback for {self.pattern=}."
                logger.error(msg)
                safe_target[key] = f"UNKNOWN_{i}"

        # Error Case 2: more values provided than keys
        if n_values > self.n_keys:
            ignoring: list[str] = target[i + 1 :]
            msg: str = f"Got {n_values=} for {self.n_keys=}! {ignoring=}."
            logger.error(msg)

        return self._namer.format(**safe_target)

    @__call__.register
    def _(self, target: str | Path) -> dict:
        """Backwards parsing name to key value pairs"""

        formatted_string: str = (
            str(target.name) if isinstance(target, Path) else str(target)
        )
        # Strip the PathGuard increment (e.g., "_1", "_42") before the extension
        clean_string = re.sub(r"_\d+(?=\.|$)", "", formatted_string)

        return self._namer.extract(clean_string)

    @classmethod
    def only_from_pattern(
        cls, pattern: str, expected_keys: list[str] | None = None
    ) -> Self:
        return cls(pattern=pattern, keys=expected_keys or [])

    @classmethod
    def with_predefined_keys(
        cls, key_indexes: list[int] | None = None
    ) -> Self:
        """Create keys and pattern factory in derived class, fill before assignment"""

        keys: list[str] = cls._load_predefined_keys()

        if key_indexes is not None:
            keys: list[str] = [keys[key_index] for key_index in key_indexes]

        pattern: str = cls._generate_predefined_pattern(keys)

        return cls(pattern=pattern, keys=keys)

    @classmethod
    def _load_predefined_keys(cls) -> list[str]:
        """Provide keys for constructor: with_predefined_keys"""
        raise NotImplementedError("Needed for ParsedName.with_predefined_keys")

    @classmethod
    def _generate_predefined_pattern(
        cls, keys: list[str], join_symbol: str = "_"
    ) -> str:
        """Some default that sometimes might be used"""
        return join_symbol.join(keys)


def parse_name_validator(value: Any) -> ParsedName:
    if isinstance(value, str):
        return ParsedName.only_from_pattern(value)
    return value


type AutoParsedName = Annotated[
    ParsedName, BeforeValidator(parse_name_validator)
]


class SstNames(BaseSettings):
    """Default names and name factories for files and project"""

    model_config = ConfigDict(extra="allow")

    project: str = ""  # INFO: must be overwritten!?

    # Master config file
    setting_file: str = "settings.json"
    # Directories in local root
    data_dir: str = "data"
    plot_dir: str = "plots"
    log_dir: str = "logs"
    _log_file_name: str = ""
    # Directories in data_dir
    local_home_dir: str = "homes"

    # Patterns

    # WARN: test if this works
    # summary_file: AutoParsedName = Field(
    #     default_factory=lambda: ParsedName(
    # WARN: test if this works
    #     )
    summary_file: AutoParsedName = ParsedName(
        pattern="{day}_summary.{suffix}",
        keys=["day", "suffix"],
    )

    @property
    def log_file(self) -> str:
        return self._log_file_name or f"{self.project}.log" or "debug.log"
