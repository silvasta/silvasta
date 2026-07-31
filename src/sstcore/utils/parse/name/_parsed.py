"""
Parse Names and Extract Keys - supported with validated BaseModel access

                                                       DependencyLevel[1]
"""

from pathlib import Path
from typing import Any

from pydantic import BaseModel

from ._base import NameParser

__all__: list[str] = [
    "ParsedName",
]

# TASK: better arg and DTO stragegy
# - so far like NameParser with a better Name,
#   at least since SchemaName exists


class ParsedName[ModelT: BaseModel](NameParser):
    """Switch bidirectional between Keywords and String"""

    model_cls: type[ModelT] | None = None  # LATER: needed?

    def __init__(
        self,
        pattern: str,
        model_cls: type[ModelT] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(pattern=pattern, **kwargs)
        self.model_cls = model_cls

    # TODO: typing for ParsedName.extract
    def extract(self, name: Path | str) -> dict[str, Any] | ModelT:  # ty:ignore
        raw: dict[str, str] = super().extract(name)  # from ExtractNormalizer
        if self.model_cls is not None:
            return self.model_cls.model_validate(raw)
        return raw
