"""
This is the initial Draft

-
"""

from collections.abc import Iterator

from ...port.color import ColorBox
from ...port.event.dto import LogDTO, PanelDTO
from ..color.box import Colors

colors: ColorBox = Colors()


class StaticToolkitMeta(type):
    """Build Metaclass for Static Toolkits with Views"""

    # IDEA: __prepare__ for auto staticmethod
    # IDEA: __init__ for inserting parameter?
    def toolkit(cls, sort: bool = True) -> list[str]:
        """Names of all staticmethods on the toolkit"""
        names: Iterator[str] = (
            name
            for name, obj in cls.__dict__.items()
            if isinstance(obj, staticmethod)
        )
        return sorted(names) if sort else list(names)

    def __str__(cls) -> str:
        return cls.__name__

    def __repr__(cls) -> str:
        statics: list[str] = cls.toolkit()
        methods: str = ", ".join(statics) if statics else "useless"
        return f"{cls}[{methods}]"

    def __rich__(cls) -> str:
        return f"{colors(cls, color=2)}"  # TODO:

    def __cli__(cls) -> PanelDTO:
        return PanelDTO(
            content=list(cls.toolkit()),
            title=cls.__rich__(),
            frame=colors.azure,  # ty:ignore
        )

    def __log__(cls) -> LogDTO:
        return LogDTO(
            message=str(cls),
            level="INFO",
            extra={"toolkit": cls.__name__},
        )

    def __call__(cls, *_, **__):
        # IDEA: just return a Path? or even better, a PathSpec confirmed Path??
        # AI: what about wiring here some Path operation?
        # - ok just for PathGuard for sure, but with an overrride?
        # - default StaticToolkit is NoReturn __call__
        # -> classes can decide to provide a minimal core functionality
        raise TypeError(f"ToolKit[{cls}] is Not available as Instance!")


def _analyze_composed_toolkit(cls):
    """cls.__dict__ does not see inherited staticmethods"""
    import inspect

    def toolkit(cls, sort: bool = True) -> list[str]:
        names: list[str] = []
        for name in dir(cls):
            if name.startswith("_"):
                continue
            obj = inspect.getattr_static(cls, name)
            if isinstance(obj, staticmethod):
                names.append(name)
        return sorted(names) if sort else names


class PathGuardMeta(StaticToolkitMeta):
    """PathGuard-specific class-level view. Construction policy inherited."""

    def __str__(cls) -> str:
        return " PathGuard "

    def __rich__(cls) -> str:
        return f"{colors.a('Path')}{colors.s('Guard')}"

    def __cli__(cls) -> PanelDTO:
        return PanelDTO(
            # REMOVE:
            content="Safety and Comfort for Path and File System operations",
            title=cls.__rich__(),
            frame="cyan",
        )
