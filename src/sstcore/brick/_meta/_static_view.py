from collections.abc import Iterator

from ...port.color import ColorBox
from ...port.event.dto import LogDTO, PanelDTO
from ..color.box import Colors

colors: ColorBox = Colors()


# NOTE: compare with util.path.guard._meta


class StaticToolkitMeta(type):
    """Build Metaclass for Static Toolkit without Init"""

    def toolkit(cls, sort=True) -> list[str]:
        """Provide Names of all staticmethods in equiped Toolkit"""
        names: Iterator[str] = (
            name
            for name, obj in cls.__dict__.items()
            if isinstance(obj, staticmethod)
        )
        return sorted(names) if sort else list(names)

    def __str__(cls) -> str:
        """FILL as desired"""
        return cls.__name__

    def __repr__(cls) -> str:
        statics: list[str] = cls.toolkit()
        methods: str = ", ".join(statics) if statics else "useless"
        return f"{cls.__name__}[{methods}]"

    def __rich__(cls) -> str:
        return f"{colors.azure(cls)}"

    def __cli__(cls) -> PanelDTO:
        return PanelDTO(
            content=list(cls.toolkit()),
            title=cls.__rich__(),
            frame=colors.azure,  # ty:ignore
        )

    def __log__(cls) -> LogDTO:
        return LogDTO(
            message=str(cls),
            # IDEA: cls.toolkit?
            level="INFO",
            extra={"toolkit": cls.__name__},
        )
