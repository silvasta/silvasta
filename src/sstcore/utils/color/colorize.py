"""
Provide convenience functions to colorize data for terminal display.

Produce Rich markup strings from Python objects with semantic coloring
based on their type, hierarchy, location and other attributes.

Functions:
    module_path: Colorize by project, modules, target of __module__

Ideas:
    Exceptions, Enums, maybe dataclass, like any special built-in type
    -> from raw to amazing to watch, track and debug in CLI
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from .box import ColorBox

c: ColorBox = ColorBox.bold()


def module_path(
    obj: Any,
    project_color: str = "cyan",
    module_color: str = "green",
    target_color: str = "special",
) -> str:
    """
    Colorize modules paths down to Object definition and up to Root

    - Process class <- map instances, handle as well functions!
    """

    target: type = obj if hasattr(obj, "__name__") else type(obj)
    raw_project, *raw_modules = target.__module__.split(".")

    project: str = c(raw_project, project_color)
    # INFO: len(modules) can be 0, consider for further color splits
    modules: list[str] = [c(module, module_color) for module in raw_modules]
    cls_or_instance = f"{c(target.__name__, target_color)}"

    return ".".join([project, *modules, cls_or_instance])


def path(target: Path) -> str:
    """Make folder parts blue and file name colored by type or white"""

    if str(target).endswith("/") or (not target.suffix and not target.name):
        return c.blue(str(target).rstrip("/") + "/")

    if target.parent != Path(".") and target.parent != Path(""):
        parent_part: str = c.blue(f"{target.parent}/")
        file_part: str = _color_file_by_type(target)
        return f"{parent_part}{file_part}"

    return _color_file_by_type(target)


FILE_COLORS: dict[str, Callable[[str], str]] = {
    # Code / Configs
    ".py": c.green,
    ".json": c.yellow,
    ".yaml": c.yellow,
    ".yml": c.yellow,
    ".md": c.cyan,
    # Images / Media
    ".png": c.magenta,
    ".jpg": c.magenta,
    ".jpeg": c.magenta,
    ".gif": c.magenta,
}


def _color_file_by_type(file_path: Path) -> str:
    """Colors the filename based on its suffix, defaulting to white."""
    suffix = file_path.suffix.lower()
    color_func = FILE_COLORS.get(suffix, c.white)
    return color_func(file_path.name)
