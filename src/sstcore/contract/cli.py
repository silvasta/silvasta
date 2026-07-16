"""
Provide typed Data Transfer Objects for the EventBus

- CliDTO: Intended for __cli__ and processed by printer

"""

from rich.align import AlignMethod

__all__: list[str] = [
    "CliDTO",
    "CliRenderable",
    "PanelDTO",
    "LineDTO",
    "TableDTO",
    "MarkdownDTO",
    "RuleDTO",
]

import warnings
from dataclasses import dataclass, field, fields
from typing import Any, ClassVar, Protocol, Self, runtime_checkable

from rich.box import ROUNDED, Box


@runtime_checkable
class CliRenderable(Protocol):
    def __cli__(self) -> CliDTO: ...


class _Dto:
    def __cli__(self) -> Self:
        return self

    def __str__(self) -> str:
        return type(self).__name__


@dataclass
class CliDTO(_Dto):
    style: str = "cyan"
    indent: int = 0
    meta: dict[str, Any] = field(default_factory=dict)

    _strict: ClassVar[bool] = False
    _content_field: ClassVar[str] = "text"

    def __post_init__(self):
        self._validate()

    def _validate(self):
        pass

    @classmethod
    def from_call(cls, target: Any = None, **kwargs) -> Self:
        """Clean args and provide DTOs for all layout methods"""

        cleaned: dict[str, Any] = cls._clean_kwargs(kwargs)
        if target is not None:
            cleaned[cls._content_field] = target

        try:
            instance: Self = cls(**cleaned)
            if instance.meta.get("unknown_args"):
                message = f"Unknown args: {instance.meta['unknown_args']}"
                if cls._strict:
                    raise TypeError(message)
                warnings.warn(message, stacklevel=2)
            return instance

        except TypeError as error:
            if cls._strict:
                raise
            cleaned.setdefault("meta", {})["error"] = str(error)
            return cls(
                **{k: v for k, v in cleaned.items() if k in cls._fields()}
            )

    @classmethod
    def _fields(cls) -> set[str]:
        return {field.name for field in fields(class_or_instance=cls)}

    @classmethod
    def _clean_kwargs(cls, kwargs: dict) -> dict[str, Any]:
        extra: dict[str, Any] = {}
        valid_fields: set[str] = cls._fields()
        for key in list(kwargs.keys()):
            if key not in valid_fields:
                extra[key] = kwargs.pop(key)
        if extra:
            kwargs.setdefault("meta", {})["unknown_args"] = extra
        return kwargs


@dataclass
class PanelDTO(CliDTO):
    text: str | list[str]  # TODO: check when normalized
    color: str = "cyan"
    frame: str = "cyan"
    title: str | None = None
    title_align: AlignMethod = "right"
    subtitle: str | None = None
    subtitle_align: AlignMethod = "right"
    box: Box = ROUNDED
    expand: bool = True
    padding: tuple = (0, 0)
    metrics: dict[str, Any] = field(default_factory=dict)

    _content_field = "text"
    _strict = True


@dataclass
class LineDTO(CliDTO):
    text: str | None = None  # For Rule = just line ----
    style: str = "cyan"
    character: str = "─"
    _content_field = "text"
    _strict = True


@dataclass
class RuleDTO(CliDTO):
    """Simple horizontal rule (the "just a line" case that got lost)."""

    style: str = "cyan"
    character: str = "─"
    _content_field = "no content..."
    _strict = True


@dataclass
class TableDTO(CliDTO):
    data: list[dict[str, Any] | list[Any]]
    headers: list[str] | None = None
    # LATER: check table setup


@dataclass
class MarkdownDTO(CliDTO):
    text: str
    header: int = 0
    style = "white"

    def _validate(self):  # LATER: which **kwargs?
        if not (0 <= (header := self.header) <= 6):
            self.header = 0
            message = f"Markdown {header=}, invalid! (H1-H6) using default=0"
            warnings.warn(message, stacklevel=2)
