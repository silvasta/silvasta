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

from ....brick.color.box import Colors
from ....brick.labor import clsname, just_return
from ....port import view
from ....port.calling import ClassRendering
from ....port.color import Color, ColorIdentifier
from ....port.event.dto import CliDTO, CliDtoCreator, LogDTO, PanelDTO
from ....port.link import portlink
from ....port.view import SstView
from ._meta_base import SstMeta, SstMetaData

colors = Colors()  # LATER: resolve this somehows


@portlink(SstView)
# @portlink(view.SstPropView)
# @portlink(view.SstShortView)
@portlink(view.SstFullView)
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

    # IMPORTANT: define better defaults!

    name: ClassRendering
    rich: ClassRendering
    cli: CliDtoCreator

    def __init__(
        self,
        name: ClassRendering | str = "",
        rich: ClassRendering | str = "",
        cli: CliDtoCreator | str = "",
        color: ColorIdentifier = Color.AZURE,
    ):
        self.name: ClassRendering = (
            name
            if isinstance(name, ClassRendering)
            else just_return(constant=name)
            if name
            else self._default_name
        )
        self.rich: ClassRendering = (
            rich
            if isinstance(rich, ClassRendering)
            else just_return(constant=rich)
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
                content=content or list(cls.toolkit()),
                title=cls.__rich__(),
                frame=colors.get(self.color),  # ty:ignore
            )

        return _default_cli
