import re
from collections.abc import Callable, Iterator
from string.templatelib import Interpolation, Template
from typing import Any, Protocol, runtime_checkable

from rich.console import Group, RenderableType
from rich.pretty import Pretty
from rich.text import Text

from ...port.view import Renderable, RichRenderable


def render_template(
    template: Template,
    *,
    default_formatter: Callable[[Any], str] = str,
) -> str:
    """Simple string rendering of a t-string."""
    parts: list[str] = []
    for item in template:
        if isinstance(item, str):
            parts.append(item)
        else:
            # Respect format spec and conversion
            value = item.value
            if item.conversion == "r":
                value = repr(value)
            elif item.conversion == "a":
                value = ascii(value)
            parts.append(format(value, item.format_spec or ""))
    return "".join(parts)


class TStringProcessor:
    def __init__(self):
        self._renderers: dict[type, Callable[[Any], Any]] = {}

    def register(self, typ: type, renderer: Callable[[Any], Any]):
        self._renderers[typ] = renderer

    def process(self, template: Template) -> list[Any]:
        """Returns a list of renderable parts (str or rich objects)."""
        result = []
        for item in template:
            if isinstance(item, str):
                result.append(item)
                continue

            value = item.value
            obj_type = type(value)

            # 1. Explicit renderer
            if obj_type in self._renderers:
                rendered = self._renderers[obj_type](value)
            # 2. Protocol-based (your existing system)
            elif isinstance(value, Renderable):
                rendered = value
            # 3. Fallback
            else:
                rendered = self._default_render(value, item)

            result.append(rendered)
        return result

    def _default_render(self, value: Any, interp: Interpolation) -> Any:
        # You can use interp.expression here for smarter decisions
        return str(value)


def smart_render(value: Any, interp: Interpolation):
    expr = interp.expression
    if expr.endswith(".path") or "path" in expr:
        return Text(str(value), style="underline green")
    if isinstance(value, int):
        return Text(str(value), style="bold yellow")
    return str(value)


def iter_parts(template: Template) -> Iterator[str | Interpolation]:
    yield from template  # empty literals already dropped by Template.__iter__


def map_template(
    template: Template, fn: Callable[[Interpolation], Interpolation]
) -> Template:
    return Template(
        *(fn(p) if isinstance(p, Interpolation) else p for p in template)
    )


def replace_values(template: Template, values: tuple[Any, ...]) -> Template:
    it = iter(values)
    return map_template(
        template,
        lambda i: Interpolation(
            next(it), i.expression, i.conversion, i.format_spec
        ),
    )


type Piece = RenderableType
type ViewFn = Callable[[Any, Interpolation], Piece]

_FORMAT_SPEC_RE = re.compile(
    r"""^
    (?:.[<>=^])?      # fill + align
    [-+ ]?            # sign
    \#?
    0?
    \d*
    [_,]?
    (?:\.\d+)?
    [bcdeEfFgGnosxX%]?
    $""",
    re.VERBOSE,
)


@runtime_checkable
class RichRenderable(Protocol):
    def __rich__(self) -> RenderableType: ...


def apply_conversion(value: Any, conversion: str | None) -> Any:
    match conversion:
        case "s":
            return str(value)
        case "r":
            return repr(value)
        case "a":
            return ascii(value)
        case _:
            return value


def looks_like_format_spec(spec: str) -> bool:
    return bool(spec) and bool(_FORMAT_SPEC_RE.match(spec))


class ViewTable:
    """Runtime type → view. Subclasses win via MRO walk."""

    def __init__(self) -> None:
        self._exact: dict[type, ViewFn] = {}

    def mount(self, target_type: type, view: ViewFn) -> None:
        self._exact[target_type] = view

    def resolve(self, obj_type: type) -> ViewFn | None:
        for cls in obj_type.__mro__:
            if cls in self._exact:
                return self._exact[cls]
        return None


DEFAULT_VIEWS = ViewTable()


def _style_text(text: str, spec: str, fallback: str) -> Text:
    return Text(text, style=spec or fallback)


def mount_builtin_views(table: ViewTable) -> None:
    table.mount(str, lambda v, i: _style_text(v, i.format_spec, "bold yellow"))
    table.mount(
        int,
        lambda v, i: (
            _style_text(
                format(v, i.format_spec or ""),
                i.format_spec and "" or "bold magenta",
                "bold magenta",
            )
            if False
            else _style_text(
                str(v),
                "" if looks_like_format_spec(i.format_spec) else i.format_spec,
                "bold magenta",
            )
        ),
    )
    table.mount(bool, lambda v, i: Text(str(v), style="green" if v else "red"))
    table.mount(type(None), lambda v, i: Text("None", style="dim italic"))


SENSITIVE = ("password", "passwd", "secret", "token", "key", "credential")


def is_sensitive(expression: str) -> bool:
    lowered = expression.lower()
    return any(part in lowered for part in SENSITIVE)


def fallback_unknown(value: Any, interp: Interpolation) -> Piece:
    """Unknown input: protocol → pretty → str, always marked as interpolated."""
    if is_sensitive(interp.expression):
        return Text("***", style="dim")
    if isinstance(value, RichRenderable):
        return value
    if hasattr(value, "__rich_console__"):
        return value
    # Entertaining, not important: compact pretty, not a full dump
    return Pretty(value, max_depth=2, max_length=8, max_string=80)


def render_interpolation(
    interp: Interpolation,
    views: ViewTable,
    unknown: ViewFn = fallback_unknown,
) -> Piece:
    value = apply_conversion(interp.value, interp.conversion)
    spec = interp.format_spec

    if interp.conversion in {"s", "r", "a"}:
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
        return view(value, interp)

    if spec:  # treat as Rich style hint on the default string form
        return Text(str(value), style=spec)

    return unknown(value, interp)


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
            pieces.append(render_interpolation(part, table, unknown))
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
