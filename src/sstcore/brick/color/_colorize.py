"""
Provide convenience functions to colorize data for terminal display.

Produce Rich markup strings from Python objects with semantic coloring
based on their type, hierarchy, location and other attributes.

Functions:
    modules: Colorize by project, modules, target of __module__

Ideas:
    Exceptions, Enums, maybe dataclass, like any special built-in type
    -> from raw to amazing to watch, track and debug in CLI
"""  # TODO: DependencyLevel

__all__: list[str] = [
    "modules",
    "path",
    # TODO: file_by_type??
]


from collections.abc import Callable
from pathlib import Path
from typing import Any

from ...port._modulepath import ModulePath
from ...port.color import ColorArg
from ..call import castarg
from .box import Colors

colors = Colors()  # CHECK: how to handle/inject?


@castarg
def modules(
    target: Any,
    /,
    project_color: ColorArg = "azure",
    module_color: ColorArg = "green",
    # LATER: qual_color, [0]-->target[-1]
    target_color: ColorArg = "purple",
) -> str:
    """
    Colorize modules paths down to Object definition and up to Root

    - Process class <- map instances, handle as well functions!
    """
    _mp = (
        target
        if isinstance(target, ModulePath)
        else ModulePath.identify(target)
    )
    return ".".join(
        (
            *([colors(_mp.project, project_color)] if _mp.project else []),
            *(colors(module, module_color) for module in _mp.submodules),
            # CHECK:colors(reflect.objname(target), target_color),
            # "-TEST-",
            *(colors(qual, target_color) for qual in _mp.quals),
        )
    )


def path(target: Path, /) -> str:
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
