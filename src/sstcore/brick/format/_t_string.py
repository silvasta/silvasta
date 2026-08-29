from collections.abc import Callable, Iterator
from string.templatelib import Interpolation, Template
from typing import Any

from ...port.view import Renderable


def iter_parts(template: Template) -> Iterator[str | Interpolation]:
    yield from template  # empty literals already dropped by Template.__iter__


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
