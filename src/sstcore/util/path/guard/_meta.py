"""Create basiv View abilities for PathGuard"""

__all__: list[str] = [
    # TODO: "PathGuardMeta",
]

from collections.abc import Iterator

from ....brick.color.box import Colors
from ....brick.meta import ToolkitMetaArgs
from ....port.color import ColorBox
from ....port.event.dto import LogDTO, PanelDTO

colors: ColorBox = Colors()

PATH_GUARD_BOOT = ToolkitMetaArgs(
    name=lambda cls: f" {cls} ",
    rich=f"{colors.azure('Path')}{colors.teal('Guard')}",
    cli="Safety and Comfort for Path and File System operations",
)


class _FormerPathGuardMeta(type):  # REMOVE: when new version works
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
        return f"{colors.a('Path')}{colors.s('Guard')}"

    def __cli__(cls) -> PanelDTO:
        return PanelDTO(
            content="Safety and Comfort for Path and File System operations",
            title=cls.__rich__(),
            frame="cyan",
        )

    def __log__(cls) -> LogDTO:
        return LogDTO(
            message=str(cls),
            level="INFO",
            metrics={"toolkit": cls.toolkit()},
        )
