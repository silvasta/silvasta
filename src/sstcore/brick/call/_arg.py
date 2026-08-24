"""
ArgDecorator - Check the Input!

-
"""

from pathlib import Path

from ...port.color import Color, ColorIdentifier
from ...port.pathguard import SyncMode
from ...utils.path.guard import PathInput, PathSpec
from ...utils.path.guard._operate import Rotate

__all__: list[str] = [
    "ArgHandler",
    "Resolver",
    "ArgCast",
    "cast_arg",
]

import functools
import inspect
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from typing import (
    Annotated,
    Any,
    Protocol,
    Self,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)


class ArgHandler[T](Protocol):
    """Functor: raw input → T. Extra kwargs are optional context."""

    def __call__(
        self,
        raw: Any,
        /,
        *,
        default: Any = inspect.Parameter.empty,
        name: str = "",
        param: inspect.Parameter | None = None,
    ) -> T: ...


@dataclass(frozen=True, slots=True)
class Resolver[T]:
    """Fill-in handler. `convert` is the only required piece."""

    convert: Callable[[Any], T]
    target: type[T] | None = None
    default: T | None = None
    use_default_on_error: bool = False
    after: Callable[[T], T] | None = None

    def accepts(self, annotation: Any) -> bool:
        if self.target is None:
            return False
        bare = get_origin(annotation) or annotation
        if bare is self.target:
            return True
        if get_origin(annotation) is Annotated:
            return self.accepts(get_args(annotation)[0])
        return False

    def __call__(
        self,
        raw: Any,
        /,
        *,
        default: Any = inspect.Parameter.empty,
        name: str = "",
        param: inspect.Parameter | None = None,
    ) -> T:
        fallback = self.default
        if default is not inspect.Parameter.empty:
            fallback = default
        try:
            value = self.convert(raw)
        except (ValueError, TypeError, KeyError) as error:
            if (
                self.use_default_on_error
                and fallback is not inspect.Parameter.empty
            ):
                return fallback  # FIX: None?
            label = self.target.__name__ if self.target else "value"
            raise ValueError(
                f"invalid {label} for {name or 'argument'!r}: {raw!r}"
            ) from error
        if self.after is not None:
            value = self.after(value)
        return value


def _hints_of(func: Callable) -> dict[str, Any]:
    try:
        return get_type_hints(func, include_extras=True)
    except Exception:
        return {}


def _handler_from_annotated(annotation: Any) -> ArgHandler | None:
    if get_origin(annotation) is not Annotated:
        return None
    for meta in get_args(annotation)[1:]:
        if callable(meta):
            return meta
    return None


@dataclass(frozen=True, slots=True)
class ArgCast:
    """Decorator Functor. Bind → resolve selected args → call.

    Fast setup:
        cast_color_args = ArgCast.types({Color: resolve_color})

    Stacked / named (PathGuard-friendly):
        @cast_arg("source", PathHandler(must_exists=True))
        @cast_arg("target", PathHandler())
        def copy(source: Path, target: Path): ...
    """

    by_type: Mapping[type, ArgHandler] = field(default_factory=dict)
    by_name: Mapping[str, ArgHandler] = field(default_factory=dict)
    annotated: bool = True

    @classmethod
    def types(
        cls, mapping: Mapping[type, ArgHandler], *, annotated: bool = True
    ) -> Self:
        return cls(by_type=mapping, annotated=annotated)

    @classmethod
    def names(cls, **handlers: ArgHandler) -> Self:
        return cls(by_name=handlers, annotated=False)

    def extend(
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

    def plan(self, func: Callable) -> dict[str, ArgHandler]:
        """Precompute param → handler. Empty plan → identity wrapper later."""
        sig = inspect.signature(func)
        hints = _hints_of(func)
        chosen: dict[str, ArgHandler] = {}
        for name, param in sig.parameters.items():
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            annotation = hints.get(name, param.annotation)
            handler = self.select(name, annotation)
            if handler is not None:
                chosen[name] = handler
        return chosen

    def __call__[**P, R](self, func: Callable[P, R]) -> Callable[P, R]:
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


def cast_arg(name: str, handler: ArgHandler) -> ArgCast:
    """One-parameter decorator. Stack one per input."""
    return ArgCast.names(**{name: handler})


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Examples
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def resolve_color(
    color_guess: ColorIdentifier, default: Color | None = None
) -> Color:
    """Map [int|str|Color] to Color or default or Raise"""
    try:
        match color_guess:
            case Color():
                return color_guess

            case int() as index:
                return Color(index)

            case str() as name:
                return Color[name.upper()]

            case _:
                raise ValueError(f"Unrecognized type: {type(color_guess)}")

    except (ValueError, KeyError) as error:
        if default is not None:
            return default
        raise ValueError(f"Map Color failed: {color_guess=}") from error


cast_color_args = ArgCast.types(
    {Color: Resolver(convert=resolve_color, target=Color)}
)


@overload
def apply_theme(primary: Color, secondary: Color = ...) -> None: ...


@overload
def apply_theme(  # ty:ignore
    primary: ColorIdentifier, secondary: ColorIdentifier = ...
) -> None: ...


@cast_color_args
def apply_theme(primary: Color, secondary: Color = Color.BLACK) -> None:
    print(f"Loaded: Primary={primary.name}, Secondary={secondary.name}")


cast_sync = ArgCast.types(
    {
        SyncMode: Resolver(SyncMode, target=SyncMode),
    }
)


@dataclass(frozen=True, slots=True)
class PathHandler:
    """Policy-bearing handler. Extra flags + optional function go here."""

    resolve: bool = False
    must_exists: bool = False
    ensure_parent: bool = False
    after: Callable[[Path], Path] | None = None  # injected behaviour

    def accepts(self, annotation: Any) -> bool:
        bare = get_origin(annotation) or annotation
        if get_origin(annotation) is Annotated:
            bare = (
                get_origin(get_args(annotation)[0]) or get_args(annotation)[0]
            )
        return bare in {Path, PathSpec} or annotation is PathInput

    def __call__(
        self,
        raw: Any,
        /,
        *,
        default: Any = inspect.Parameter.empty,
        name: str = "",
        param: inspect.Parameter | None = None,
    ) -> Path:
        path = PathSpec.ok(
            target=raw,
            resolve=self.resolve,
            must_exists=self.must_exists,
        )
        if self.ensure_parent:
            path.parent.mkdir(parents=True, exist_ok=True)
        if self.after is not None:
            path = self.after(path)
        return path


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Stack
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@overload
def copy(
    source: Path, target: Path, mode: SyncMode = SyncMode.INCREMENT
) -> Path: ...


@overload
def copy(
    source: Any, target: Any, mode: SyncMode = SyncMode.INCREMENT
) -> Path: ...


@cast_arg("source", PathHandler(must_exists=True, resolve=True))
@cast_arg("target", PathHandler())
@cast_arg("mode", Resolver(SyncMode, target=SyncMode))
def copy(
    source: Path,
    target: Path,
    mode: SyncMode = SyncMode.INCREMENT,
) -> Path:
    return Rotate.synced(source=source, target=target, mode=mode)


path_op = ArgCast.names(
    source=PathHandler(must_exists=True, resolve=True),
    target=PathHandler(),
).extend(by_type={SyncMode: Resolver(SyncMode, target=SyncMode)})


@path_op
def rotate(
    source: Path,
    target: Path,
    sync_mode: SyncMode = SyncMode.INCREMENT,
    reset: bool = False,
) -> Path:
    raise NotImplementedError


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Annotated
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

Source = Annotated[PathInput, PathHandler(must_exists=True, resolve=True)]
Target = Annotated[PathInput, PathHandler()]


@ArgCast()  # annotated=True by default
def _rotate(
    source: Source, target: Target, sync_mode: SyncMode = SyncMode.INCREMENT
) -> Path:
    raise NotImplementedError


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Cast
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@dataclass(frozen=True, slots=True)
class PathCast(ArgCast):
    """PathGuard-internal decorator. Override select(), nothing else."""

    def select(self, name: str, annotation: Any) -> ArgHandler | None:
        if name in {"source", "src"}:
            return self.by_name.get(name, PathHandler(must_exists=True))
        if name in {"target", "dst"}:
            return self.by_name.get(name, PathHandler())
        return super().select(name, annotation)
