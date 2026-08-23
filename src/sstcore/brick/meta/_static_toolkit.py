"""
Shape the Blueprint for Toolkits equipped with Static Functions

StaticFuncMeta
 - auto-convert public methods in class body to staticmethod
 - attach customizable views with defaults

StaticFuncMetaData


"""

__all__: list[str] = [
    "StaticFuncMeta",
    "StaticFuncMetaData",
]


import inspect
from types import FunctionType
from typing import TYPE_CHECKING, Any

from ...port.call import ClassRendering
from ...port.color import Color, ColorBox, ColorIdentifier
from ...port.event.dto import CliDTO, LogDTO, PanelDTO
from ...port.event.dto._produce import CliDtoCreator
from ...port.shape import Meta, MetaData
from ..color._arg import resolve_color
from ..color.box import Colors
from ..format import cls_name, reflect

colors: ColorBox = Colors()  # ty:ignore


class StaticFuncMeta(type):
    """Create Blueprint for Static Functorials"""

    _data: StaticFuncMetaData

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: StaticFuncMetaData | None = None,
    ):
        """Attach all methods as staticmethod and load input for dunder data"""
        new_static_methods: dict[str, Any] = {
            key: staticmethod(value)
            for key, value in namespace.items()
            if not key.startswith("_") and isinstance(value, FunctionType)
        }
        namespace.update(new_static_methods)

        cls = super().__new__(mcls, name, bases, namespace)

        cls._data = data or StaticFuncMetaData()

        return cls

    def __cli__(cls) -> CliDTO:
        return cls._data.cli(cls)

    def __str__(cls) -> str:
        return cls._data.name(cls)

    def __rich__(cls) -> str:
        return cls._data.rich(cls)

    def __repr__(cls) -> str:
        return f"{cls.__name__}[{', '.join(cls.toolkit()) or 'useless'}]"

    def __log__(cls) -> LogDTO:
        return LogDTO(
            message=str(cls),
            level="INFO",
            metrics={"toolkit": cls.toolkit()},
            extra={"toolkit": repr(cls)},
        )

    def __call__(cls, *_, **__) -> Any:
        # NOTE: candidate for _data.call
        # TODO: route the Error here
        raise TypeError(f"StaticFunc[{cls}] is Not available as Instance!")

    def toolkit(cls, sort: bool = True) -> list[str]:
        """Provide names of all public staticmethods"""
        # LATER: candidate for format.reflect
        # Parameter:
        # - public/private
        # - {static|class}method|property, what else?
        names: list[str] = [
            name
            for name in dir(cls)
            if not name.startswith("_")
            and isinstance(inspect.getattr_static(cls, name), staticmethod)
        ]
        return sorted(names) if sort else names


class StaticFuncMetaData:
    """InputSpace, Defaults, Pre-processing -> finally data container"""

    name: ClassRendering
    rich: ClassRendering
    cli: CliDtoCreator
    color: Color

    def __init__(
        self,
        name: ClassRendering | str = "",
        rich: ClassRendering | str = "",
        cli: CliDtoCreator | str = "",
        color: ColorIdentifier = Color.AZURE,
    ):
        self.color: Color = resolve_color(color_guess=color)

        self.name: ClassRendering = (
            name
            if isinstance(name, ClassRendering)
            else reflect.just_return(constant=name)
            if name
            else self._default_name
        )

        self.rich: ClassRendering = (
            rich
            if isinstance(rich, ClassRendering)
            else reflect.just_return(constant=rich)
            if rich
            else self._default_rich
        )

        self.cli: CliDtoCreator = (
            cli
            if isinstance(cli, CliDtoCreator)
            else self._default_cli_loader(content=cli)
        )

    def _default_name(self, cls) -> str:
        return cls_name(cls)

    def _default_rich(self, cls) -> str:
        return colors(cls, self.color)

    def _default_cli_loader(self, content: str) -> CliDtoCreator:
        def _default_cli(cls) -> CliDTO:
            return PanelDTO(
                content=content or list(cls.toolkit()),
                title=cls.__rich__(),
                frame=colors.get(self.color),
            )

        return _default_cli


if TYPE_CHECKING:
    _cls_meta: type[Meta] = StaticFuncMeta
    _cls_data: type[MetaData] = StaticFuncMetaData
    _instance_data: MetaData = StaticFuncMetaData()
