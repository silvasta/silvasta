from string.templatelib import Template
from typing import Any

from sstcore.port.view import CliRenderable, Renderable, RichRenderable


def tstring_to_renderables(
    template: Template,
    *,
    unknown_handler: str = "rich_yellow",  # or "str", "repr", "debug"
    registry: dict[type, Any] | None = None,
) -> list[Renderable]:
    registry = registry or {}
    result: list[Renderable] = []

    for item in template:
        if isinstance(item, str):
            result.append(item)
            continue

        # item is Interpolation
        obj = item.value
        obj_type = type(obj)

        # 1. Registry (highest priority - custom views)
        if obj_type in registry:
            handler = registry[obj_type]
            if callable(handler):
                result.append(handler(obj))
            else:
                result.append(handler)
            continue

        # 2. Existing protocols you already defined
        if isinstance(obj, RichRenderable) or hasattr(obj, "__rich__"):
            result.append(obj)
            continue
        if isinstance(obj, CliRenderable) or hasattr(obj, "__cli__"):
            result.append(obj.__cli__())
            continue

        # 3. Unknown object strategy
        if unknown_handler == "rich_yellow":
            from rich.text import Text

            result.append(Text(str(obj), style="bold yellow"))
        elif unknown_handler == "debug":
            from rich.text import Text

            label = f"{item.expr}={obj!r}"
            result.append(Text(label, style="dim red"))
        elif unknown_handler == "repr":
            result.append(repr(obj))
        else:  # "str"
            result.append(str(obj))

    return result


# Adapter for your printer
def render_template(
    template: Template, /, **spec: Unpack[PrintSpec]
) -> CliDTO:
    renderables = tstring_to_renderables(
        template, unknown_handler="rich_yellow"
    )
    # Call your existing normalized printer engine
    return printer_engine(*renderables, **spec)
