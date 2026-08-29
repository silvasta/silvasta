from collections.abc import Callable
from string.templatelib import Interpolation, Template
from typing import Any

from rich.console import Group, RenderableType
from rich.pretty import Pretty
from rich.text import Text

from ...port.view import RichRenderable, Stringable
from ._t_norm import Conversion, is_sensitive, looks_like_format_spec
from ._t_table import Piece, ViewFn, ViewTable


def fallback_unknown(value: Any, item: Interpolation) -> Piece:
    """Unknown input: protocol → pretty → str, always marked as itemolated."""
    if is_sensitive(item.expression):
        return Text("***", style="dim")
    if isinstance(value, RichRenderable):
        return value
    if hasattr(value, "__rich_console__"):
        return value
    # Entertaining, not important: compact pretty, not a full dump
    return Pretty(value, max_depth=2, max_length=8, max_string=80)


def replace_values(template: Template, values: tuple[Any, ...]) -> Template:
    it = iter(values)
    return map_template(
        template,
        lambda i: Interpolation(
            next(it), i.expression, i.conversion, i.format_spec
        ),
    )


def map_template(
    template: Template, fn: Callable[[Interpolation], Interpolation]
) -> Template:
    return Template(
        *(fn(p) if isinstance(p, Interpolation) else p for p in template)
    )


def sanitize(template: Template, max_str: int = 120) -> Template:
    def wrap(i: Interpolation) -> Interpolation:
        v = i.value
        if is_sensitive(i.expression):
            v = "***"
        elif isinstance(v, str) and len(v) > max_str:
            v = v[: max_str - 1] + "…"
        return Interpolation(v, i.expression, i.conversion, i.format_spec)

    return map_template(template, wrap)


def render_plain(template: Template) -> str:
    parts: list[str] = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
            continue
        value: Stringable = Conversion._t(item)
        spec: str = item.format_spec
        try:
            parts.append(
                format(value, spec)
                if spec and looks_like_format_spec(spec)
                else str(value)
            )
        except TypeError, ValueError:
            parts.append(str(value))
    return "".join(parts)


def render_interpolation(
    item: Interpolation,
    views: ViewTable,
    unknown: ViewFn = fallback_unknown,
) -> Piece:
    value: Stringable = Conversion._t(item)
    spec = item.format_spec

    if item.conversion in {"s", "r", "a"}:
        text = str(value)
        if looks_like_format_spec(spec):
            text = format(text, spec)
            spec = ""
        return Text(text, style=spec or "bold yellow")

    if looks_like_format_spec(spec):
        try:
            return Text(format(value, spec), style="bold yellow")
        except TypeError, ValueError:
            pass

    view = views.resolve(type(value))
    if view is not None:
        return view(value, item)

    if spec:  # treat as Rich style hint on the default string form
        return Text(str(value), style=spec)

    return unknown(value, item)


def template_to_pieces(
    template: Template,
    views: ViewTable | None = None,
    unknown: ViewFn = fallback_unknown,
) -> list[Piece]:
    table = views or DEFAULT_VIEWS
    pieces: list[Piece] = []
    for part in template:
        if isinstance(part, str):
            pieces.append(Text(part))
        else:
            pieces.append(render_itemolation(part, table, unknown))
    return pieces


def t_string_render(
    template: Template,
    /,
    *,
    views: ViewTable | None = None,
    unknown: ViewFn = fallback_unknown,
) -> RenderableType:
    pieces = template_to_pieces(template, views, unknown)
    if all(isinstance(p, Text) for p in pieces):
        out = Text()
        for p in pieces:
            out.append_text(p)  # type: ignore[arg-type]
        return out
    return Group(*pieces)
