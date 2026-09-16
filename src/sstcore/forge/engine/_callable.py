"""
Provide

FunctorMeta
  - attach views and instance names
  - insert hybrid dispatch into the namespace when asked
  - class-call of Hybrid forwards to a prototype instance

FunctorMetaData
  - views, color
  - hybrid flag + overridable apply/wrap/delay/detect/reject/__call__
"""

__all__: list[str] = [
    "FunctorMeta",
    "FunctorMetaData",
]


import functools
from collections.abc import Callable
from types import FunctionType
from typing import TYPE_CHECKING, Any, NoReturn

from ...port.call import ClassRendering
from ...port.color import Color, ColorBox, ColorIdentifier
from ...port.event.dto import CliDTO, CliDtoCreator, LogDTO, PanelDTO
from ...port.shape import Meta, MetaData
from ..color._arg import resolve_color
from ..color.box import Colors
from ..format import clsname, reflect

colors: ColorBox = Colors()  # ty:ignore

_SPAWN_KEYS: frozenset[str] = frozenset({"func", "detect", "reject"})


def hybrid_detect(self, target: object) -> bool:
    raise NotImplementedError(f"{type(self).__name__} needs detect()", target)


def hybrid_reject(self, fail: object, *args: Any, **kwargs: Any) -> NoReturn:
    emit = getattr(self, "emit", None)
    if callable(emit):
        emit("Invalid Hybrid Usage", fail, *args, **kwargs)
    raise TypeError("Invalid Hybrid Usage", fail)


def hybrid_apply(self, value: Any, /, *args: Any, **kwargs: Any) -> Any:
    func = getattr(self, "_func", None)
    if not func:
        raise NotImplementedError("Provide func or override apply!")
    return func(value, *args, **kwargs)


def hybrid_wrap(self, fn: Callable, /, *args: Any, **kwargs: Any) -> Callable:
    @functools.wraps(fn)
    def wrapper(*fn_args: Any, **fn_kwargs: Any) -> Any:
        return self.apply(fn(*fn_args, **fn_kwargs), *args, **kwargs)

    return wrapper


def hybrid_delay(self, *args: Any, **kwargs: Any) -> Callable:
    return lambda fn: self.wrap(fn, *args, **kwargs)


def hybrid_call(
    self, target: object = None, /, *args: Any, **kwargs: Any
) -> Any:
    """Triple dispatch: apply / wrap / delay."""
    if self.detect(target):
        return self.apply(target, *args, **kwargs)
    if callable(target) and not isinstance(target, type):
        return self.wrap(target, *args, **kwargs)
    if target is None:
        return self.delay(*args, **kwargs)
    return self.reject(target)


def _as_static(fn: Callable) -> staticmethod | Callable:
    if isinstance(fn, (staticmethod, classmethod)):
        return fn
    if isinstance(fn, FunctionType):
        return staticmethod(fn)
    return fn


class FunctorMeta(type):
    """Create Blueprint for Active Functorials"""

    _data: "FunctorMetaData"

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: "FunctorMetaData | None" = None,
    ):
        """Insert hybrid methods, then load dunder data"""
        data = data or FunctorMetaData()
        data.prepare(namespace)

        cls = super().__new__(mcls, name, bases, namespace)
        cls._data = data
        return cls

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        return cls._data.enter(cls, args, kwargs)

    def spawn(cls, *args: Any, **kwargs: Any) -> Any:
        """Always construct an instance (skip hybrid class-dispatch)."""
        instance = type.__call__(cls, *args, **kwargs)
        cls._data.bind_instance(instance)
        return instance

    def __cli__(cls) -> CliDTO:
        return cls._data.cli(cls)

    def __str__(cls) -> str:
        return cls._data.name(cls)

    def __rich__(cls) -> str:
        return cls._data.rich(cls)

    def __repr__(cls) -> str:
        kind = "Hybrid" if cls._data.hybrid else "Functor"
        return f"{kind}[{cls.__name__}]"

    def __log__(cls) -> LogDTO:
        return LogDTO(
            message=str(cls),
            level="INFO",
            extra={"kind": "hybrid" if cls._data.hybrid else "simple"},
        )


class FunctorMetaData:
    """InputSpace, Defaults, Pre-processing -> finally data container"""

    name: ClassRendering
    rich: ClassRendering
    cli: CliDtoCreator
    color: Color
    hybrid: bool

    def __init__(
        self,
        name: ClassRendering | str = "",
        rich: ClassRendering | str = "",
        cli: CliDtoCreator | str = "",
        color: ColorIdentifier = Color.AZURE,
        hybrid: bool = False,
        *,
        apply: Callable | None = None,
        wrap: Callable | None = None,
        delay: Callable | None = None,
        detect: Callable | None = None,
        reject: Callable | None = None,
        call: Callable | None = None,
    ):
        self.hybrid = hybrid
        self.color: Color = resolve_color(color_guess=color)

        self.name: ClassRendering = (
            name
            if isinstance(name, ClassRendering)
            else reflect.just_return(constant=name)
            if name
            else self._default_name
        )
        self.rich: ClassRendering = (
            rich
            if isinstance(rich, ClassRendering)
            else reflect.just_return(constant=rich)
            if rich
            else self._default_rich
        )
        self.cli: CliDtoCreator = (
            cli
            if isinstance(cli, CliDtoCreator)
            else self._default_cli_loader(content=cli)
        )

        # class body > these inserts > defaults
        self._insert: dict[str, Any] = {}
        if hybrid:
            self._insert = {
                "apply": _as_static(apply) if apply else hybrid_apply,
                "wrap": wrap or hybrid_wrap,
                "delay": delay or hybrid_delay,
                "detect": _as_static(detect) if detect else hybrid_detect,
                "reject": reject or hybrid_reject,
                "__call__": call or hybrid_call,
            }

    def prepare(self, namespace: dict[str, Any]) -> None:
        for key, impl in self._insert.items():
            namespace.setdefault(key, impl)

    def enter(self, cls: type, args: tuple, kwargs: dict) -> Any:
        if not self.hybrid or _SPAWN_KEYS & kwargs.keys():
            instance = type.__call__(cls, *args, **kwargs)
            self.bind_instance(instance)
            return instance
        return self.prototype(cls)(*args, **kwargs)

    def prototype(self, cls: type) -> Any:
        proto = vars(cls).get("_proto")
        if proto is None:
            proto = cls.spawn()
            cls._proto = proto
        return proto

    def bind_instance(self, instance: Any) -> None:
        """__name__ / wrapper metadata. Called after __init__."""
        func = getattr(instance, "_func", None)
        hint = getattr(instance, "_name_hint", "")
        if callable(func):
            functools.update_wrapper(instance, func, updated=())
        if hint or not getattr(instance, "__name__", None):
            name = hint or reflect.func(
                func, default=f"{clsname(type(instance))}Unit"
            )
            instance.__name__ = name
            instance.__qualname__ = name

    def _default_name(self, cls) -> str:
        return clsname(cls)

    def _default_rich(self, cls) -> str:
        return colors(cls, self.color)

    def _default_cli_loader(self, content: str) -> CliDtoCreator:
        def _default_cli(cls) -> CliDTO:
            return PanelDTO(
                content=content or ("hybrid" if self.hybrid else "simple"),
                title=cls.__rich__(),
                frame=colors.get(self.color),
            )

        return _default_cli


if TYPE_CHECKING:
    _cls_meta: type[Meta] = FunctorMeta
    _cls_data: type[MetaData] = FunctorMetaData
    _instance_data: MetaData = FunctorMetaData()
