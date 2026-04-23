import re
from datetime import datetime
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

    def _forward_parsing(
        self,
        clean_target: dict[str, str],  # , *args, **kwargs
    ) -> str:
        """Used for override and intercept in StyledName"""
        return self._namer.format(**clean_target)

    def forward_parsing(
        self,
        safe_target: dict[
            str, str | datetime  # maybe | Path ?
        ],
    ) -> str:
        """Final cleanup of string befor extracting keys with PatternNamer"""

        clean_target: dict[str, str] = {}

        for key, val in safe_target.items():
            if isinstance(val, datetime):
                # MOVE: how to apply? seperate function, attribute?
                val = f"{val:%Y-%m-%d_%H-%M-%S}"

            # TODO: what else? apply any checkup here,
            # maybe as easily overridable function

            clean_target[key] = val

        return self._forward_parsing(clean_target)

    def backwards_parsing(self, formatted_string: str) -> dict:
        """Final cleanup of string befor extracting pattern with PatternNamer"""

        # Strip PathGuard increments (e.g., "_1", "_42") before the extension
        clean_string: str = re.sub(r"_\d+(?=\.|$)", "", formatted_string)

        return self._namer.extract(clean_string)

    @singledispatchmethod
    def __call__(self, target):
        raise NotImplementedError(f"Cannot process {type(target)=}, {target=}")

    @__call__.register
    def _(self, target: dict) -> str:
        """Forward parsing, key value pairs to safe dict"""

        # Ensure every key required by the pattern exists in the target dict
        safe_target: dict = {}

        for key in self.keys:
            if key not in target:
                msg: str = f"Missing value for {key=}! Using fallback for: {self.pattern=}"
                logger.error(msg)
                safe_target[key] = f"UNKNOWN-{key.upper()}"
            else:
                safe_target[key] = target[key]

        return self.forward_parsing(safe_target)

    @__call__.register
    def _(self, target: list) -> str:
        """Forward parsing, value list to safe dict"""

        # Ensure every key required by the pattern exists in the target dict
        safe_target: dict = {}
        n_values: int = len(target)

        for i, key in enumerate(self.keys):
            if i < n_values:
                safe_target[key] = target[i]

            # Error Case 1: less values provided than keys
            if i >= n_values:
                msg: str = f"Missing value for {key=}! Using fallback for: {self.pattern=}"
                logger.error(msg)
                safe_target[key] = f"UNKNOWN-STYLE{i}"

        # Error Case 2: more values provided than keys
        if n_values > self.n_keys:
            ignoring: list[str] = target[i + 1 :]
            msg: str = f"Got {n_values=} for {self.n_keys=}! {ignoring=}."
            logger.error(msg)

        return self.forward_parsing(safe_target)

    @__call__.register
    def _(self, target: Path) -> dict:
        """Backwards parsing name to key value pairs"""

        return self.backwards_parsing(target.name)

    @__call__.register
    def _(self, target: str) -> dict:
        """Backwards parsing name to key value pairs"""

        return self.backwards_parsing(str(target))

    @classmethod
    def only_from_pattern(
        cls, pattern: str, expected_keys: list[str] | None = None
    ) -> Self:
        return cls(pattern=pattern, keys=expected_keys or [])

    @staticmethod
    # TODO: dispach with list
    def format_brackets(key: str) -> str:
        return f"{{{key}}}"  # needed for proper {key}

    @classmethod
    def with_predefined_keys(
        cls, key_indexes: list[int] | None = None
    ) -> Self:
        """Create keys and pattern factory in derived class, fill before assignment"""

        raw_keys: list[str] = cls._load_predefined_keys()

        if key_indexes is None:
            keys: list[str] = raw_keys
        else:
            keys: list[str] = [raw_keys[i] for i in key_indexes]

        pattern: str = cls._generate_predefined_pattern(keys)

        logger.debug(f"{pattern=}, {keys=}")

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

        # TODO: dispach with list
        bracket_keys: list[str] = [cls.format_brackets(key) for key in keys]

        return join_symbol.join(bracket_keys)


def parse_name_validator(value: Any) -> ParsedName:
    if isinstance(value, str):
        return ParsedName.only_from_pattern(value)
    return value


class StyledName(ParsedName):
    style_pattern: str
    styles: list[str]

    _styler: PatternNamer = PrivateAttr()
    _styled: bool = PrivateAttr(default=False)

    def _sync_styler_and_styles(self):
        """Runs automatically whenever the model is instantiated or updated."""

        rich_template: str = self.style_pattern

        for i, style in enumerate(self.styles, start=1):
            rich_template: str = rich_template.replace(f"{{style{i}}}", style)

        self._styler = PatternNamer(rich_template)
        logger.info(f"{self._styler=}")

    def _forward_parsing(self, clean_target: dict[str, str]) -> str:
        """Used for override and intercept in StyledName"""

        if self._styled:
            return self._styler.format(**clean_target)
        else:
            return self._namer.format(**clean_target)

    def styled(self, target: dict | list) -> str:

        self._styled = True
        self._sync_styler_and_styles()

        rich_string: str = self(target)

        return rich_string

    @classmethod
    def parse_style(
        cls, style_pattern: str, keys: list[str], styles: list[str]
    ) -> Self:
        """Use transfromed style_pattern as base pattern for regex parser setup"""

        pattern: str = re.sub(r"\[.*?\]", "", style_pattern)

        return cls(
            pattern=pattern,
            keys=keys,
            style_pattern=style_pattern,
            styles=styles,
        )


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
    summary_file: AutoParsedName = ParsedName(
        pattern="{day}_summary.{suffix}",
        keys=["day", "suffix"],
    )
    sstfile_dates: StyledName = StyledName.parse_style(
        style_pattern="[{style1}]{name}[/]: [{style2}]{first_tracked}[/] - [{style3}]{last_updated}[/]",
        keys=["name", "first_tracked", "last_updated"],
        styles=["blue", "dim", "white"],
    )

    @property
    def log_file(self) -> str:
        return self._log_file_name or f"{self.project}.log" or "debug.log"
