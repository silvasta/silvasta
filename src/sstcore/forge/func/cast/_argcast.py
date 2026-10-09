"""
ArgDecorator - Check the Input!

-
"""

__all__: list[str] = [
    "ArgHandler",
    "ArgCast",
]

import functools
import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from typing import Annotated, Any, Self, get_args, get_origin, get_type_hints

from ._port import ArgHandler


@dataclass(frozen=True, slots=True)
class ArgCast:
    # AI_TASK: which are actually needed?
    # - by_name is error prone
    # - by_type could work e.g. for the BaseEnum family
    # - by_annotation is probably the plan
    by_type: Mapping[type, ArgHandler] = field(default_factory=dict)
    by_name: Mapping[str, ArgHandler] = field(default_factory=dict)
    annotated: bool = True

    @classmethod  # REMOVE: ??
    def types(
        cls, mapping: Mapping[type, ArgHandler], *, annotated: bool = True
    ) -> Self:
        return cls(by_type=mapping, annotated=annotated)

    @classmethod  # REMOVE: ??
    def names(cls, **handlers: ArgHandler) -> Self:
        return cls(by_name=handlers, annotated=False)

    def extend(  # REMOVE:??
        self,
        *,
        by_type: Mapping[type, ArgHandler] | None = None,
        by_name: Mapping[str, ArgHandler] | None = None,
        annotated: bool | None = None,
    ) -> Self:
        return replace(
            self,
            by_type={**self.by_type, **(by_type or {})},
            by_name={**self.by_name, **(by_name or {})},
            annotated=self.annotated if annotated is None else annotated,
        )

    def select(self, name: str, annotation: Any) -> ArgHandler | None:
        # MERGE: _get_caster
        """Override in a subclass to add matching rules (PathCast, …)."""
        if name in self.by_name:
            return self.by_name[name]
        if self.annotated:
            found = _handler_from_annotated(annotation)
            if found is not None:
                return found
        bare = get_origin(annotation) or annotation
        if bare in self.by_type:
            return self.by_type[bare]
        for handler in self.by_type.values():
            accepts = getattr(handler, "accepts", None)
            if accepts is not None and accepts(annotation):
                return handler
        return None

    def plan(self, func: Callable[..., Any]) -> dict[str, ArgHandler]:
        # MERGE: _get_plan
        sig = inspect.signature(func)
        hints = get_type_hints(func, include_extras=True)
        out: dict[str, ArgHandler] = {}
        for name, param in sig.parameters.items():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            handler = self.select(name, hints.get(name, param.annotation))
            if handler is not None:
                out[name] = handler
        return out

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
        # MERGE: cast_args
        sig = inspect.signature(func)
        handlers = self.plan(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            if not handlers:
                return func(*args, **kwargs)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for name, handler in handlers.items():
                param = sig.parameters[name]
                bound.arguments[name] = handler(
                    bound.arguments[name],
                    default=param.default,
                    name=name,
                    param=param,
                )
            return func(*bound.args, **bound.kwargs)

        return wrapper


def _handler_from_annotated(annotation: Any) -> ArgHandler | None:
    if get_origin(annotation) is not Annotated:
        return None
    for meta in get_args(annotation)[1:]:
        if callable(meta):
            return meta
    return None
