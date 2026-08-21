"""
Construct the Shape of StaticToolkit Classes

-
"""

__all__: list[str] = [
    "StaticToolkitMeta",
    "ToolkitMetaArgs",
    "ClsRendering",  # MOVE: to port when needed at second location
]


import inspect
from collections.abc import Callable
from types import FunctionType
from typing import Any, Protocol, runtime_checkable

from ...port.color import Color, ColorBox, ColorIdentifier
from ...port.event.dto import CliDTO, LogDTO, PanelDTO
from ..color._arg import resolve_color
from ..color.box import Colors
from ..format import cls_name

colors: ColorBox = Colors()


def just_return[Target](constant: Target) -> Callable[..., Target]:
    def constant_function(*_, **__) -> Target:
        return constant

    return constant_function  # MOVE: to sstcore.brick.format|func


@runtime_checkable
class CliDtoFactory(Protocol):
    # NEXT:
    # NEXT:
    # NEXT:
    # MOVE: to sstcore.port.event.dto
    def __call__(self, cls: type) -> CliDTO: ...


@runtime_checkable  # REMOVE: runtime check useful? dangerous?
class ClsRendering(Protocol):  # NOTE: keep until second usage appears
    def __call__(self, cls: type) -> str: ...


class ToolkitMetaArgs:
    """Define ArgSpace, defaults, pre-filter and provide rendering"""

    name: ClsRendering
    rich: ClsRendering
    cli: CliDtoFactory
    color: Color

    def __init__(
        self,
        name: ClsRendering | str = "",
        rich: ClsRendering | str = "",
        cli: CliDtoFactory | str = "",
        color: ColorIdentifier = Color.AZURE,
    ):
        self.color: Color = resolve_color(color_guess=color)

        self.name: ClsRendering = (
            name
            if isinstance(name, ClsRendering)
            else just_return(constant=name)
            if name
            else self._default_name
        )

        self.rich: ClsRendering = (
            rich
            if isinstance(rich, ClsRendering)
            else just_return(constant=rich)
            if rich
            else self._default_rich
        )

        self.cli: CliDtoFactory = (
            cli
            if isinstance(cli, CliDtoFactory)
            else self._default_cli_loader(content=cli)
        )

    def _default_name(self, cls) -> str:
        return cls_name(cls)

    def _default_rich(self, cls) -> str:
        return colors(cls, self.color)

    def _default_cli_loader(self, content: str) -> CliDtoFactory:
        def _default_cli(cls) -> CliDTO:
            return PanelDTO(
                content=content or list(cls.toolkit()),
                title=cls.__rich__(),
                frame=colors.get(self.color),
            )

        return _default_cli


class StaticToolkitMeta(type):
    """Build Metaclass for Static Toolkit without Init"""

    _data: ToolkitMetaArgs

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *_,
        data: ToolkitMetaArgs | None = None,
        **__,
    ):

        new_static_methods: dict[str, Any] = {
            key: staticmethod(value)
            for key, value in namespace.items()
            if not key.startswith("_") and isinstance(value, FunctionType)
        }
        namespace.update(new_static_methods)

        cls = super().__new__(mcls, name, bases, namespace)

        cls._data = data or ToolkitMetaArgs()

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
            extra={"toolkit": cls.toolkit()},
        )

    def __call__(cls, *_, **__) -> Any:  # NOTE: candidate for _data.call
        raise TypeError(f"ToolKit[{cls}] is Not available as Instance!")

    def toolkit(cls, sort: bool = True) -> list[str]:
        """Provide names of all public staticmethods"""
        names: list[str] = [  # NEXT: candidate for format.reflect
            name
            for name in dir(cls)
            if not name.startswith("_")
            and isinstance(inspect.getattr_static(cls, name), staticmethod)
        ]
        return sorted(names) if sort else names
