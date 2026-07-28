"""Create basiv View abilities for PathGuard"""

__all__: list[str] = [
    "PathGuardMeta",
]

from collections.abc import Iterator

from ....contract.cli import PanelDTO
from ....contract.log import LogDTO
from ...color import ColorBox

c: ColorBox = ColorBox.bold()


class PathGuardMeta(type):
    """Let PathGuard execute the regular instance dunders"""

    def toolkit(cls, sort=True) -> list[str]:
        """Provide Names of all staticmethods in equiped Toolkit"""
        names: Iterator[str] = (
            name
            for name, obj in cls.__dict__.items()
            if isinstance(obj, staticmethod)
        )
        return sorted(names) if sort else list(names)

    def __str__(cls) -> str:
        return " PathGuard "

    def __repr__(cls) -> str:
        statics: list[str] = cls.toolkit()
        methods: str = ", ".join(statics) if statics else "useless"
        return f"{cls.__name__}[{methods}]"

    def __rich__(cls) -> str:
        return f"{c.cyan('Path')}{c.magenta('Guard')}"

    def __cli__(cls) -> PanelDTO:
        return PanelDTO(
            text="Safety and Comfort for Path and File System operations",
            title=cls.__rich__(),
            frame="cyan",
        )

    def __log__(cls) -> LogDTO:
        return LogDTO(
            message=str(cls),
            level="INFO",
            metrics={"toolkit": cls.toolkit()},
        )
