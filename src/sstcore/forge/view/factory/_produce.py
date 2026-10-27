"""
Prepare Functors, 1 per DTO

- add optional safe mode
- handle stacked functions

"""

__all__: list[str] = [
    "LogDtoProducer",
    "CliDtoProducer",
    "PanelDtoProducer",
    "MarkdownDtoProducer",
    "LineDtoProducer",
    "TableDtoProducer",
]

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Self, Unpack

from ....port import functorial
from ....port.color import Color, ColorArg
from ....port.event import dto
from ....port.event._param import _Boxes
from ....port.link import portlink
from ....port.represent import Stringable
from ...func import SafeFunctor
from ._table import TableViewDTO


@portlink(functorial.MountableFunctor)
class DtoProducer[DTO: dto.EventDTO = dto.EventDTO](SafeFunctor[..., DTO]):
    """Assemble the DTO - handle variations"""

    dto_name: dto.DtoNames

    def __init__(self, registry: dto.DtoTable[DTO], **kwargs):  # DTO:Any
        self._registry: dto.DtoTable[DTO] = registry
        super().__init__(**kwargs)

    @property
    def dto_cls(self) -> type[DTO]:
        return self._registry[self.dto_name]

    @classmethod
    def __mount__(cls, host: Any, /, *, name: str = "", **kwargs: Any) -> Self:
        return cls(registry=host._registry, name=name, **kwargs)

    # @classmethod
    # CHECK: undesired:
    # def __mount__(cls, host: Any, /, *, name: str = "", **kwargs: Any) -> Self:
    #     registry = getattr(host, "_registry", None) or getattr(
    #         getattr(host, "dto", None), "_registry", dto.EventDTO._registry)
    #     sink = host if callable(host) else None
    #     colors = getattr(host, "colors", None)
    #     return cls(
    #         registry=registry,
    #         sink=sink,
    #         colors=colors,
    #         name=name,
    #         **kwargs,
    #     )


#  LINE: -- Log and Cli Base -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LogDtoProducer(DtoProducer[dto.LogDTO]):
    dto_name: dto.DtoNames = "log"

    def __call__(
        self, message: str, /, **kwargs: Unpack[dto.LogInput]
    ) -> dto.LogDTO:
        return self.dto_cls.create(message=message, **kwargs)


class CliDtoProducer(DtoProducer[dto.CliDTO]):
    dto_name: dto.DtoNames = "cli"

    def __call__(
        self, content: Sequence[dto.CliSpec], /, **kwargs: Unpack[dto.CliInput]
    ) -> dto.CliDTO:
        return self.dto_cls.create(tuple(content), **kwargs)


#  LINE: -- Cli Specifications -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PanelDtoProducer(DtoProducer[dto.PanelDTO]):
    dto_name: dto.DtoNames = "panel"

    def __call__(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.PanelInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(*content, **kwargs)


class BoxDtoProducer(DtoProducer[dto.PanelDTO]):
    # REMOVE: this is not a DtoProducer! this is rendering information!!
    """Mid-level structural functor for Box variations (`box`, `box.up`, `box.mini`, etc.)."""

    dto_name: dto.DtoNames = "panel"

    def __call__(
        self,
        *content: dto.CliSpec,
        box: _Boxes = _Boxes.OPEN,
        **kwargs: Unpack[dto.BoxInput],
    ) -> dto.PanelDTO:
        return self.dto_cls.create(content, box=box, **kwargs)

    def open(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(content, box=_Boxes.OPEN, **kwargs)

    def round(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(content, box=_Boxes.ROUND, **kwargs)

    def corner(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(content, box=_Boxes.CORNER, **kwargs)

    def up(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(content, box=_Boxes.UP, **kwargs)

    def down(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(content, box=_Boxes.DOWN, **kwargs)

    def mini(
        self,
        *content: dto.CliSpec,
        mode: Literal["up", "down", "both"] = "both",
        **kwargs: Unpack[dto.BoxInput],
    ) -> dto.PanelDTO:
        match mode:
            case "up":
                selected = _Boxes.MINI_UP
            case "down":
                selected = _Boxes.MINI_DOWN
            case "both":
                selected = _Boxes.MINI
        return self.dto_cls.create(content, box=selected, **kwargs)

    def mini_up(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(content, box=_Boxes.MINI_UP, **kwargs)

    def mini_down(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.BoxInput]
    ) -> dto.PanelDTO:
        return self.dto_cls.create(content, box=_Boxes.MINI_DOWN, **kwargs)


class HeaderDtoProducer(DtoProducer[dto.PanelDTO]):
    # REMOVE: this is not a DtoProducer! this is rendering information!!
    """High-level functor for standalone banners or titled content panels."""

    dto_name: dto.DtoNames = "panel"

    def __call__(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.HeaderPresetInput],
    ) -> dto.PanelDTO:
        return self.dto_cls.create(content, title=title, **kw)

    def dip(
        self,
        head: str,
        text: str,
        *content: dto.CliSpec,
        color: ColorArg = Color.AZURE,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO:
        """Highlight `head` in `color` followed by `text`, framed in `color`."""
        # REMOVE: no _colors on DtoProducer!!
        styled_title = f"{self._colors(head, color)} {text}"
        return self.dto_cls.create(
            content, title=styled_title, color=color, **kw
        )


@portlink(functorial.MountableFunctor)
class StatusDtoProducer(DtoProducer[dto.PanelDTO]):
    # NEXT: what is that??
    # REMOVE:
    """Parametrized semantic preset functor (success, warn, danger, special, info)."""

    dto_name: dto.DtoNames = "panel"

    def __init__(
        self,
        registry: dto.DtoTable[dto.PanelDTO],
        *,
        default_color: Color = Color.AZURE,
        default_topic: str = "",
        **kwargs: Any,
    ) -> None:
        super().__init__(registry, **kwargs)
        self._default_color: Color = default_color
        self._default_topic: str = default_topic

    def __call__(
        self,
        title: str,
        *content: dto.CliSpec,
        **kw: Unpack[dto.StatusInput],
    ) -> dto.PanelDTO:
        merged: dict[str, Any] = dict(kw)
        if self._default_topic and "topic" not in merged:
            merged["topic"] = self._default_topic
            merged.setdefault("topic_color", self._default_color)
        return self.dto_cls.create(
            content, title=title, color=self._default_color, **merged
        )


class MarkdownDtoProducer(DtoProducer[dto.MarkdownDTO]):
    dto_name: dto.DtoNames = "markdown"

    def __call__(
        self, content: Stringable, /, **kwargs: Unpack[dto.MarkdownInput]
    ) -> dto.MarkdownDTO:
        return self.dto_cls.create(content, **kwargs)


class LineDtoProducer(DtoProducer[dto.LineDTO]):
    dto_name: dto.DtoNames = "line"

    def __call__(
        self, *content: dto.CliSpec, **kwargs: Unpack[dto.LineInput]
    ) -> dto.LineDTO:
        return self.dto_cls.create(content, **kwargs)

    def len(
        # REMOVE: this is clearly rendering information!
        # IMPORTANT: capture this here by regular call
        # - the Renderer prepares this information and calls the Producer with that
        self,
        name: str,
        *content: dto.CliSpec | Sequence[dto.CliSpec],
        **kw: Unpack[dto.LinePresetInput],
    ) -> dto.LineDTO:
        """
        Render lines with an automatic `<name>: <count>` header.

        Accepts either `line.len("Files", file_list)` or `line.len("Files", "a", "b")`.
        """
        if (
            len(content) == 1
            and isinstance(content[0], Sequence)
            and not isinstance(content[0], (str, bytes))
        ):
            items: tuple[dto.CliSpec, ...] = tuple(content[0])
        else:
            items = tuple(
                c
                for c in content
                if not isinstance(c, Sequence) or isinstance(c, str)
            )  # type: ignore[arg-type]

        header_title = f"{name}: {len(items)}"
        merged: dict[str, Any] = dict(kw)
        merged.setdefault("header_topic", name)
        return self.dto_cls.create(
            items,
            title=header_title,
            stat=lambda vec: f"{name}: {len(vec)}",
            **merged,
        )


class TableDtoProducer(DtoProducer[TableViewDTO]):
    dto_name: dto.DtoNames = "table"

    def __call__(
        self,
        content: dto._Grid,
        /,
        **kwargs: Unpack[dto.TableInput],
    ) -> TableViewDTO:
        return self.dto_cls.create(content, **kwargs)

    # IMPORTANT: the methods defined in _table are valid extensions for the Producer
    # - it might be possible that the TableViewDTO is dropped and just the functor applies the methods
    # - for now, keep it

    # AI_TASK: check the inputs of the dto upgrade
    # - Sequence triggered some warnings and list is probably fine for now

    def matrix(
        self,
        matrix: Sequence[Sequence[dto.CliSpec]],
        /,
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_matrix(matrix, **kw)

    def rows(
        self,
        rows: Mapping[str, dto.CliSpec | Sequence[dto.CliSpec]],
        /,
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_rows(rows, **kw)

    def cols(
        self,
        cols: Mapping[str, Sequence[Any]],
        /,
        *,
        corner: str = "",
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self._emit(self.dto_cls.from_cols(cols, corner=corner, **kw))

    def records(
        self,
        records: Sequence[Mapping[str, Any]],
        /,
        *,
        headers: Sequence[str] | None = None,
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self._emit(
            self.dto_cls.from_records(records, headers=headers, **kw)
        )

    def kv(
        self,
        mapping: Mapping[str, Any],
        /,
        *,
        key_col: str = "Key",
        val_col: str = "Value",
        **kw: Unpack[dto.TablePresetInput],
    ) -> TableViewDTO:
        return self.dto_cls.from_kv(
            mapping, key_col=key_col, val_col=val_col, **kw
        )
