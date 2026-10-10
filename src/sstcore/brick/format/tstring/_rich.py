"""
T-string rendering for rich

-
"""

from string.templatelib import Interpolation, Template

from rich.console import Group, RenderableType
from rich.pretty import Pretty
from rich.text import Text

from ....port.calling import Richable, Stringable
from ._base import Conversion, is_sensitive, looks_like_format_spec
from ._definition import ViewTable


def render_interpolation(item: Interpolation, /, views: ViewTable):
    value: Stringable = Conversion.map(item)
    spec = item.format_spec

    if looks_like_format_spec(spec):
        try:
            return Text(format(value, spec), style="bold yellow")
        except TypeError, ValueError:
            pass

    if view := views.resolve(type(value)):
        return view(value, item)

    if spec:
        return Text(str(value), style=spec)

    return fallback_unknown(value, item)


def template_to_pieces(
    template: Template, views: ViewTable
) -> list[RenderableType]:
    pieces: list[RenderableType] = []
    for part in template:
        if isinstance(part, str):
            pieces.append(Text(part))
        else:
            pieces.append(render_interpolation(part, views))
    return pieces


def render_tstring(
    template: Template, /, *, views: ViewTable
) -> RenderableType:
    pieces: list[RenderableType] = template_to_pieces(template, views)
    if all(isinstance(p, Text) for p in pieces):
        out = Text()
        for p in pieces:
            out.append_text(p)  # ty:ignore
        return out
    return Group(*pieces)


def fallback_unknown(value: Stringable, item: Interpolation) -> RenderableType:

    if is_sensitive(item.expression):
        return Text("***", style="dim")

    if isinstance(value, Richable):
        return str(value)

    return Pretty(value, max_depth=2, max_length=8, max_string=80)
