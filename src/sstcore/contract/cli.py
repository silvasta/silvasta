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


class _DtoBase:
    def __cli__(self) -> Self:
        return self

    def __str__(self) -> str:
        return type(self).__name__


@dataclass(kw_only=True)
class CliDTO(_DtoBase):
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


@dataclass(kw_only=True)
class PanelDTO(CliDTO):
    text: str | list[str]  # TODO: check when normalized
    color: str = "bold white"
    frame: str = "cyan"  # TODO: share normalize! done in print.mixin.layout
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


@dataclass(kw_only=True)
class LineDTO(CliDTO):
    text: str | None = None  # For Rule = just line ----
    style: str = "cyan"
    character: str = "─"
    _content_field = "text"
    _strict = True


@dataclass(kw_only=True)
class RuleDTO(CliDTO):
    """Dedicated horizontal rule."""

    char: str = "─"
    style: str = "cyan"
    _content_field = "char"
    _strict = False


@dataclass(kw_only=True)
class TableDTO(CliDTO):
    """Store Table data as lists of rows containing lists of values"""

    matrix: list[list[Any]]  # The Content [1:][1:]

    col_names: list[str] = field(default_factory=list)  # [0][1:] (header)
    row_names: list[str] = field(default_factory=list)  # [1:][0]
    corner: str = ""  # [0][0] element: used if Row and Col names Defined

    def _validate(self):
        if not self.matrix:  # LATER: confirm that empty is valid
            return
        if self.col_names:
            if (n_col := len(self.col_names)) != (w := len(self.matrix[0])):
                raise ValueError(f"{n_col} row_names but matrix width ({w})")
        if self.row_names:
            if (n_row := len(self.row_names)) != (h := len(self.matrix)):
                raise ValueError(f"{n_row} row_names but matrix height ({h})")

    @property
    def header(self) -> list[str]:
        """Yields the complete header row, including the corner if needed."""
        return (
            []
            if not self.col_names
            else self.col_names
            if not self.row_names
            else [self.corner] + self.col_names
        )

    @property
    def rows(self):
        """Yield aligned rows and inject side-titles if needed"""
        for i, row in enumerate(self.matrix):
            if self.row_names and i < len(self.row_names):
                # LATER: colorize, zip(strict=True)
                yield [self.row_names[i]] + row
            else:
                yield row

    @classmethod
    def from_row_dicts(cls, rows: dict[str, list[Any]]) -> Self:
        """Transform dict of {row_name: values} to internal structure."""
        return cls(
            matrix=list(rows.values()),
            row_names=list(rows.keys()),
        )

    # WARN: missing  regular args,kwargs!

    @classmethod
    def from_col_dicts(cls, cols: dict[str, list[Any]]) -> Self:
        """Transform dict of {col_name: values} to internal structure."""
        return cls(  # Transpose columns into rows using zip
            matrix=[list(row) for row in zip(*cols.values(), strict=True)],
            col_names=list(cols.keys()),
        )

    @classmethod
    def from_col_list(cls, cols: list[list[Any]]) -> Self:
        """Transform list of columns to internal row structure."""
        return cls(matrix=[list(row) for row in zip(*cols, strict=True)])

    @classmethod
    def from_value_dicts(
        cls, rows: list[dict[str, Any]], headers: list[str] | None = None
    ) -> Self:
        """Transform list of dicts [{"Header A": 1, "Header B": 2}]"""
        if not rows:
            return cls(matrix=[])
        if headers is None:
            headers: list[str] = list(
                # dict.fromkeys acts as ordered set
                dict.fromkeys(k for row in rows for k in row.keys())
            )
        filtered_matrix: list[list[Any]] = [
            # Build, filter and sort the matrix by header
            [row.get(header, "") for header in headers]
            for row in rows
        ]
        return cls(matrix=filtered_matrix, col_names=headers)


@dataclass(kw_only=True)
class MarkdownDTO(CliDTO):
    text: str
    header: int = 0
    style = "white"

    def _validate(self):  # LATER: which **kwargs?
        if not (0 <= (header := self.header) <= 6):
            self.header = 0
            message = f"Markdown {header=}, invalid! (H1-H6) using default=0"
            warnings.warn(message, stacklevel=2)
