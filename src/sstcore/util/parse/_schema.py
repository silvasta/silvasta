"""
Transform to BaseModel and Merge with Registries and Files

- Remaining NameParser after the Package moved to sstcore.format...

                                                       DependencyLevel[0]
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from ...brick.name import NameParser

__all__: list[str] = [
    "SchemaName",
]


class SchemaName(BaseModel, NameParser):
    """Hold and validate Pattern and Keys to Generate or Extract Names"""

    pattern: str
    keys: tuple[str, ...] = Field(default_factory=tuple)

    strip_extension: bool = False
    strip_increments: bool = False
    datetime_format: str = "%Y-%m-%d_%H-%M-%S"

    _regex: Any = PrivateAttr()

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        validate_assignment=True,
        from_attributes=True,
    )

    def model_post_init(self, __context: Any) -> None:
        """Runs exactly once after the model is initialized."""
        self.update_pattern(self.pattern)
