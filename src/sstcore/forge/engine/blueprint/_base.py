"""
Construct Components, Bases and MetaMixins

- Prepare Views for (Static) Blueprints

"""

__all__: list[str] = [
    "SstMeta",
    "SstMetaData",
    # view
    "MetaViewBase",
    "MetaViewData",
]

from collections.abc import Callable
from typing import Any

from ....brick.color._arg import resolve_color
from ....brick.color.box import Colors
from ....brick.labor import clsname, just_return
from ....port.calling import ClassRendering
from ....port.color import Color, ColorIdentifier
from ....port.event.dto import CliDTO, CliDtoCreator, LogDTO, PanelDTO

colors = Colors()  # LATER: resolve this somehows


class SstMetaData:
    """Level 0 Mdto"""

    color: Color

    def __init__(self, color: ColorIdentifier = Color.AZURE):
        self.color: Color = resolve_color(color_guess=color)


class SstMeta(type):
    """Level 0 Meta"""

    _data_class: type[SstMetaData] = SstMetaData  # RENAME: _dto? or _dtc?
    _data: SstMetaData

    # TODO: check SstMeta.__init__?

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: SstMetaData | None = None,
        **kwargs,
    ):
        cls = super().__new__(
            mcs,
            name,
            bases,
            namespace,
            # TASK: forward kwargs??
            # - maybe keep it open for custom changes
            # - on the other side why do this here?
            # - maybe just emit when kwargs not empty?
            # similar for potential SstMeta.__init__?
            **kwargs,
        )

        cls._data = data or mcs._data_class()

        return cls


class MetaViewData(SstMetaData):
    """Base DTO for Class-Level Views."""

    name: ClassRendering
    rich: ClassRendering
    cli: CliDtoCreator

    def __init__(
        self,
        name: ClassRendering | str = "",
        rich: ClassRendering | str = "",
        cli: CliDtoCreator | str = "",
        color: ColorIdentifier = Color.AZURE,  # LATER: define defaults
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


class MetaViewBase(SstMeta):  # WARN: base works now but don't overmix it...!
    """Provide all Views for Classes"""

    _data_class: type[MetaViewData] = MetaViewData
    # TASK: find better way for default cls
    _data: MetaViewData

    toolkit: Callable[[], list[str]]

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: MetaViewData | None = None,
        **kwargs,
    ):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        cls._data = data or mcs._data_class()

        return cls

    # AI:_QUESTION: why use _data after __new__ / during entire process?
    # - not that it should be deleted, but what is the issue with attach?
    # - meaning that the functions get transfered to the class in __new__
    # what about some kind of descriptor? is that possible for (meta-)classees?
    # -> that would allow same control as if one would modify _data

    def __cli__(cls) -> CliDTO:
        return cls._data.cli(cls)

    def __str__(cls) -> str:
        return cls._data.name(cls)

    def __rich__(cls) -> str:
        return cls._data.rich(cls)

    def __repr__(cls) -> str:
        # LATER: find solution for toolkit,
        # maybe in static base? or from format
        return f"{clsname(cls)}[{', '.join(cls.toolkit()) or 'useless'}]"

    def __log__(cls) -> LogDTO:
        return LogDTO(
            message=str(cls),
            level="INFO",
            metrics={"toolkit": cls.toolkit()},
            extra={"toolkit": repr(cls)},
        )
