from ..port.cli import PanelDTO
from ..port.log import LogDTO
from ..utils.color import ColorBox

c: ColorBox = ColorBox.bold()


class StaticToolkitMeta(type):
    """
    Reusable Metaclass for Static Toolkits.

    - Check PathGuardMeta for improvements

    """

    # NOTE:- Check PathGuardMeta for improvements

    def __str__(cls) -> str:
        return f"{cls.__name__} Toolkit"

    def __repr__(cls) -> str:
        # Defaults to a generic subtitle if the class doesn't define one
        subtitle = getattr(cls, "_toolkit_subtitle", "Static utility toolkit")
        return f"<{cls.__name__}: {subtitle}>"

    def __rich__(cls) -> str:
        # Dynamically fetch the color method from ColorBox, defaulting to blue
        color_name = getattr(cls, "_toolkit_color", "blue")
        color_func = getattr(c, color_name, c.blue)
        return color_func(cls.__name__)

    def __cli__(cls) -> PanelDTO:
        # Use the class docstring as the panel text, with a fallback
        doc = cls.__doc__ or "Provides static utility operations."
        frame_color = getattr(cls, "_toolkit_color", "blue")

        return PanelDTO(
            text=doc.strip(),
            title=cls.__rich__(),
            frame=frame_color,
            title_align="right",
        )

    def __log__(cls) -> LogDTO:
        return LogDTO(
            message=str(cls),
            level="INFO",
            extra={"toolkit": cls.__name__},
        )
