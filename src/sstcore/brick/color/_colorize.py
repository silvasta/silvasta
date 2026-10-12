"""
Provide convenience functions to colorize data for terminal display.

Produce Rich markup strings from Python objects with semantic coloring
based on their type, hierarchy, location and other attributes.

Functions:
    modules: Colorize by project, modules, target of __module__

Ideas:
    Exceptions, Enums, maybe dataclass, like any special built-in type
    -> from raw to amazing to watch, track and debug in CLI
"""

__all__: list[str] = [
    "modules",
    "path",
]

# NEXT: make this modular feature stack of ColorBox


from collections.abc import Callable
from pathlib import Path
from typing import Any

from ...port.color import ColorArg
from .. import reflect
from ..call import castarg
from .box import Colors

colors = Colors()

_x: list[Any] = reflect.dict.full(colors)


@castarg
def modules(
    target: Any,
    /,
    project_color: ColorArg = "azure",
    module_color: ColorArg = "green",
    target_color: ColorArg = "purple",
) -> str:
    """
    Colorize modules paths down to Object definition and up to Root

    - Process class <- map instances, handle as well functions!
    """

    module: str = reflect.attr.module(target, default="builtins")
    _raw_project, *_raw_modules = module.split(".")

    project: str = colors(_raw_project, project_color)
    modules: list[str] = [
        colors(module, module_color) for module in _raw_modules
    ]
    cls_or_instance = f"{colors(reflect.objname(target), target_color)}"

    return ".".join((project, *modules, cls_or_instance))


def path(target: Path) -> str:
    """Make folder parts blue and file name colored by type or white"""

    if str(target).endswith("/") or (not target.suffix and not target.name):
        return colors.blue(str(target).rstrip("/") + "/")

    if target.parent != Path(".") and target.parent != Path(""):
        parent_part: str = colors.blue(f"{target.parent}/")
        file_part: str = file_by_type(target)
        return f"{parent_part}{file_part}"

    return file_by_type(target)


FILE_COLORS: dict[str, Callable[[str], str]] = {
    ".py": colors.slate,
    ".rs": colors.slate,
    # Configs
    ".json": colors.white,
    ".log": colors.white,
    #
    ".yaml": colors.yellow,
    ".yml": colors.yellow,
    ".md": colors.carbon,
    # Images / Media
    ".png": colors.purple,
    ".jpg": colors.purple,
    ".jpeg": colors.purple,
    ".gif": colors.purple,
}


def file_by_type(file_path: Path, /) -> str:
    """Colors the filename based on its suffix, defaulting to white."""
    suffix: str = file_path.suffix.lower()
    if color_func := FILE_COLORS.get(suffix):
        return color_func(file_path.name)
    return file_path.name
