"""
Shape the Blueprint for Functors acting in different Spaces

FunctorMeta
  - ...

"""

__all__: list[str] = [
    "FunctorMeta",
    "FunctorMetaData",
]

import functools
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeGuard

from ....port.color import Color, ColorIdentifier
from ....port.functor import ErrorPolicy
from ....port.shape import Meta, MetaData
from ...color._arg import resolve_color
from ...format import cls_name, reflect


class FunctorMeta[MaybeUsefulT](type):
    """Create Blueprint for Active Functorials"""

    _data: FunctorMetaData

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: FunctorMetaData | None = None,
    ):
        cls = super().__new__(mcls, name, bases, namespace)
        cls._data = data or FunctorMetaData()

        # TODO: __name__,__qualname__, see brick.func
        # TODO: emit?

        if extract_detect := reflect.dig(cls, attrs=["detect"]):
            # TODO: add better
            cls._data.detect = extract_detect

        return cls

    def __call__(cls, *args, **kwargs):
        """The Hybrid Triple Dispatch (Class-Level)"""

        target = args[0] if args else None

        # CASE 1: Direct Execution -> MyFunctor("data")
        # We use the MetaData's detect function to type-guard the input.
        if (
            target is not None
            and cls._data.detect
            and cls._data.detect(target)
        ):
            # Instantiate a throwaway instance to execute the logic
            instance = super().__call__(**kwargs)
            return instance.apply(target, *args[1:], **kwargs)

        # CASE 2: Bare Decorator -> @MyFunctor
        if callable(target) and not isinstance(target, type):
            instance = super().__call__()
            instance._func = target
            instance.config = kwargs
            functools.update_wrapper(instance, target)
            return instance

        # CASE 3: Parameterized Decorator -> @MyFunctor(config="value")
        if not args and kwargs:
            instance = super().__call__()
            instance._func = None
            instance.config = kwargs
            return instance

        raise TypeError(  # TODO: check _hybrid
            f"Invalid Hybrid Dispatch for {cls_name(cls)}. Target: {target}"
        )


class FunctorMetaData:
    """Collect..."""

    def _default_xxx(self) -> Any:
        raise NotImplementedError

    def __init__(
        self,
        name: str = "",
        color: ColorIdentifier = Color.AZURE,
        # TASK: parametrize detect
        detect: Callable[[Any], TypeGuard[Any]] | None = None,
        policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE,
    ):
        self.color: Color = resolve_color(color_guess=color)
        self.name: str = name
        self.detect: Callable[[Any], TypeGuard[Any]] | None = detect
        self.policy: ErrorPolicy = policy


if TYPE_CHECKING:
    _cls_meta: type[Meta] = FunctorMeta
    _cls_data: type[MetaData] = FunctorMetaData
    _instance_data: MetaData = FunctorMetaData()
