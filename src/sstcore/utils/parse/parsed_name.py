import re
from datetime import datetime
from functools import singledispatchmethod
from pathlib import Path
from typing import Any, Self

from loguru import logger
from pydantic import BaseModel, Field, PrivateAttr, model_validator

from ...exceptions import NotImplementedDispatchError
from .regex import PatternNamer


class ParsedName[ModelT: BaseModel](BaseModel):
    pattern: str
    _namer: PatternNamer = PrivateAttr()
    keys: list[str] = Field(default_factory=list)

    model_cls: type[ModelT] | None = Field(default=None, exclude=True)

    strip_extension: bool = Field(default=False)
    datetime_format: str = Field(default="%Y-%m-%d_%H-%M-%S", exclude=True)

    @property
    def n_keys(self) -> int:
        return len(self.keys)

    def forward_parsing(self, safe_target: dict[str, str | datetime]) -> str:

        clean_target: dict[str, str] = {}

        for key, val in safe_target.items():
            if isinstance(val, datetime):
                val = f"{val:{self.datetime_format}}"
            clean_target[key] = val

        return self._forward_parsing(clean_target)

    def _forward_parsing(self, clean_target: dict[str, str]) -> str:
        """Used for override and interception in StyledName"""
        return self._namer.format(**clean_target)

    def backwards_parsing(
        self, formatted_string: str
    ) -> dict[str, Any] | ModelT:

        # Strip PathGuard increments (e.g., "_1", "_42") before the extension
        clean_string: str = re.sub(r"_\d+(?=\.|$)", "", formatted_string)

        raw_dict: dict = self._namer.extract(clean_string)

        if self.model_cls:
            return self.model_cls(**raw_dict)

        return raw_dict

    @singledispatchmethod
    def __call__(self, target: Any):
        raise NotImplementedDispatchError(target)

    @__call__.register
    def _(self, target: dict) -> str:
        """Forward parsing, key value pairs to safe dict"""

        safe_target: dict = {}

        for key in self.keys:
            if key not in target:
                logger.error(
                    f"Missing value for {key=}!"
                    " Using fallback for: {self.pattern=}"
                )
                safe_target[key] = f"UNKNOWN-{key.upper()}"
            else:
                safe_target[key] = target[key]

        return self.forward_parsing(safe_target)

    @__call__.register
    def _(self, target: list | tuple) -> str:
        """Forward parsing, value list to safe dict"""

        safe_target: dict = {}
        n_values: int = len(target)

        for i, key in enumerate(self.keys):
            if i < n_values:
                safe_target[key] = target[i]

            # Error Case 1: less values provided than keys -> Fill
            if i >= n_values:
                logger.error(
                    f"Missing value for {key=}!"
                    " Using fallback for: {self.pattern=}"
                )
                safe_target[key] = f"UNKNOWN-STYLE{i}"

        # Error Case 2: more values provided than keys -> Crop
        if n_values > self.n_keys:
            ignoring = target[i + 1 :]
            msg: str = f"Got {n_values=} for {self.n_keys=}! {ignoring=}"
            logger.error(msg)

        return self.forward_parsing(safe_target)

    # TASK: backwards parsing of list that doesn't throw!

    @__call__.register
    def _(self, target: Path) -> dict[str, Any] | ModelT:
        """Backwards parsing name to key value pairs or BaseModel"""
        target_str: str = target.stem if self.strip_extension else target.name
        return self.backwards_parsing(target_str)

    @__call__.register
    def _(self, target: str) -> dict[str, Any] | ModelT:
        """Backwards parsing name to key value pairs or BaseModel"""
        return self.backwards_parsing(target)

    @singledispatchmethod
    @staticmethod  # LATER: format_brackets[T] and  -> T | list[T]:
    def format_brackets(target: str | list[str]):
        raise NotImplementedDispatchError(target)

    @staticmethod
    def _format_brackets(key: str) -> str:
        """Needed for proper {key}"""
        return f"{{{key}}}"

    @format_brackets.register
    @staticmethod
    def _(target: str) -> str:
        return ParsedName._format_brackets(key=target)

    @format_brackets.register
    @staticmethod
    def _(target: list) -> list[str]:
        return [ParsedName._format_brackets(key) for key in target]

    @classmethod
    def with_predefined_keys(
        cls, key_indexes: list[int] | None = None
    ) -> Self:
        """Use key and pattern factory in derived class for constructor"""

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
        """Some Defaults that might be used sometimes"""
        return join_symbol.join(cls.format_brackets(keys))

    @model_validator(mode="after")
    def _sync_namer_and_keys(self) -> Self:
        """Runs automatically whenever the model is instantiated or updated."""
        self._namer = PatternNamer(self.pattern)

        # 1. If schema provided, auto-populate keys from the model fields
        if self.model_cls and not self.keys:
            self.keys: list[str] = list(self.model_cls.model_fields.keys())

        # 2. Validation check against the pattern
        if self.keys and set(self.keys) != set(self._namer.keys):
            logger.error(
                f"Configured pattern '{self.pattern}' changed expected keys! "
                f"Expected: {self.keys}, Found: {self._namer.keys}. "
                f"Generated strings might contain 'UNKNOWN' placeholders."
            )
        # Sync to the actual keys requested by the pattern
        self.keys: list[str] = self._namer.keys

        return self
