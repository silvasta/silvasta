"""
Construct Components, Bases and MetaMixins

- Prepare Views for (Static) Blueprints

"""

from typing import Any

__all__: list[str] = [
    "ClsViewBase",
    "ClsViewData",
]

from collections.abc import Callable

from ...brick.call import just_return
from ...brick.color.box import Colors
from ...brick.reflect import clsname
from ...port import represent
from ...port.calling import ClsRendering
from ...port.color import Color, ColorId
from ...port.event.dto import CliDTO, CliDtoCreator, LogDTO, PanelDTO
from ...port.link import portlink
from ...port.represent import SstView
from ._meta_base import SstMeta, SstMetaData

colors = Colors()


@portlink(SstView)
@portlink(represent.SstView)
class ClsViewBase(SstMeta):
    """Provide all Views for Classes"""

    toolkit: Callable[[], list[str]]
    _data: ClsViewData

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: ClsViewData,
    ):
        cls = super().__new__(mcs, name, bases, namespace, data)

        cls._data = data

        return cls

    def __cli__(cls) -> CliDTO:  # noqa:N805
        return cls._data.cli(cls)

    def __str__(cls) -> str:  # noqa:N805
        return cls._data.name(cls)

    def __rich__(cls) -> str:  # noqa:N805
        return cls._data.rich(cls)

    def __repr__(cls) -> str:  # noqa:N805
        # LATER: find solution for toolkit, maybe in static base? or from format
        return f"{clsname(cls)}[{', '.join(cls.toolkit()) or 'useless'}]"

    def __log__(cls) -> LogDTO:  # noqa:N805
        return LogDTO(
            message=str(cls),
            level="INFO",
            metrics={"toolkit": cls.toolkit()},
            extra={"toolkit": repr(cls)},
        )


class ClsViewData(SstMetaData):
    """Base DTO for Class-Level Views."""

    # IMPORTANT: improve defaults!

    name: ClsRendering
    rich: ClsRendering
    cli: CliDtoCreator

    def __init__(
        self,
        name: ClsRendering | str = "",
        rich: ClsRendering | str = "",
        cli: CliDtoCreator | str = "",
        color: ColorId = Color.AZURE,
    ):
        self.name: ClsRendering = (
            name
            if isinstance(name, ClsRendering)
            else just_return(name)
            if name
            else self._default_name
        )
        self.rich: ClsRendering = (
            rich
            if isinstance(rich, ClsRendering)
            else just_return(rich)
            if rich
            else self._default_rich
        )
        self.cli: CliDtoCreator = (
            cli
            if isinstance(cli, CliDtoCreator)
            else self._default_cli_loader(content=cli)
        )
        super().__init__(color)  # TODO: here or at beginning?

    def _default_name(self, cls) -> str:
        return clsname(cls)

    def _default_rich(self, cls) -> str:
        return colors(cls, self.color)

    def _default_cli_loader(self, content: str) -> CliDtoCreator:
        """Produce Views for the MetaVievBase"""

        def _default_cli(cls) -> CliDTO:
            return PanelDTO(
                content=content or cls.toolkit(),  # FIX:
                title=cls.__rich__(),
                frame=Color.resolve(self.color),
            )

        return _default_cli
