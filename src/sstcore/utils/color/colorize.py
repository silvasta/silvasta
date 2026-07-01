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

from typing import Any

from .box import ColorBox

c: ColorBox = ColorBox.bold()


def module_path(
    any: Any,
    project_color: str = "cyan",
    module_color: str = "green",
    target_color: str = "special",
) -> str:
    """
    Colorize modules paths down to Object definition and up to Root

    - Process class <- map instances, handle as well functions!
    """

    # TEST: colorize functions, check how that works

    target: type = any if hasattr(any, "__name__") else type(any)
    raw_project, *raw_modules = target.__module__.split(".")

    project: str = c(raw_project, project_color)
    modules: list[str] = [c(module, module_color) for module in raw_modules]
    cls_or_instance = f"{c(target.__name__, target_color)}"

    return ".".join([project, *modules, cls_or_instance])
