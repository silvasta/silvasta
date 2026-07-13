from pathlib import Path
from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, model_validator

from .base import NameParser


class SchemaName(NameParser, BaseModel):
    """
    Pydantic-native name parser.

    The model fields drive the keys. The class can be used both as
    a validator (TreeNameSchema("t_42_math.json")) and as a parser.

    This is the "melting" version you asked for – it integrates
    cleanly with the existing BaseModel registries in Sachmis.

    Usage in sachmis/config/names.py:

        class TreeNameSchema(SchemaName):
            pattern: ClassVar[str] = "t_{tree_id}_{topic}"
            tree_id: int
            topic: str

        # Then:
        schema = TreeNameSchema.from_name(path)          # explicit
        schema = TreeNameSchema(path)                    # auto via validator
        name_str = schema.to_name()                      # round-trip
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        validate_assignment=True,
        from_attributes=True,
    )

    # Class-level parser cache (one per concrete subclass)
    # REMOVE: no class attach to pydantic, parser=self!!!!!!
    _parser: ClassVar[NameParser | None] = None

    @model_validator(mode="before")
    @classmethod
    def _parse_name_if_string(cls, data: Any) -> Any:
        if isinstance(data, (str, Path)):
            return cls.from_name(data).model_dump()
        return data

    @classmethod
    def _get_parser(cls) -> NameParser:
        if cls._parser is None and hasattr(cls, "pattern"):
            cls._parser = NameParser(
                pattern=cls.pattern,
                strip_extension=True,
                strip_increments=False,  # important for IDs
            )
        if cls._parser is None:
            raise AttributeError(f"{cls.__name__} has no .pattern")
        return cls._parser

    @classmethod
    def from_name(cls, name: str | Path) -> Self:
        """Primary constructor from filesystem name."""
        parser = cls._get_parser()
        parsed_dict = parser.extract(name)  # uses the raw pipeline
        return cls.model_validate(parsed_dict)

    def to_name(self) -> str:
        """Render back to a filename (raw)."""
        return self._get_parser().format(self.model_dump())

    def __str__(self) -> str:
        return self.to_name()

    def __rich__(self) -> str:
        return f"[cyan]{self.__class__.__name__}[/]: {self.to_name()}"
