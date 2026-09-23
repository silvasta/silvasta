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

from loguru import logger

from ....brick.labor import clsname
from ....port.functor import ErrorPolicy
from ....port.shape import Meta, MetaData
from ._base import MetaViewBase, MetaViewData


class FunctorMetaData(MetaViewData):
    """Collect Policy and input check"""

    detect: Callable[[Any], TypeGuard[Any]] | None
    catch: Callable[[Exception, Any], Any] | None
    policy: ErrorPolicy
    exit_code: int

    def __init__(
        self,
        detect: Callable[[Any], TypeGuard[Any]] | None = None,
        catch: Callable[[Exception, Any], Any] | None = None,
        policy: ErrorPolicy = ErrorPolicy.LOG_AND_CONTINUE,
        exit_code: int = 1,
        **kwargs,
    ):
        self.detect = detect
        self.catch = catch
        self.policy = policy
        self.exit_code = exit_code
        super().__init__(**kwargs)


class FunctorMeta[MaybeUsefulT](MetaViewBase):
    """Create Blueprint for Active Functorials"""

    _data_class = FunctorMetaData
    _data: FunctorMetaData

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: FunctorMetaData | None = None,
        **kwargs,
    ):
        # MOVE: probably SstMeta (or intermediate mixin)
        if "emit" not in namespace:
            # MOVE: maybe new forge.blueprint._defaults
            def default_emit(self, *args, **kwargs) -> None:
                logger.debug(*args, **kwargs)

            namespace["emit"] = default_emit

        # AI_QUESTION: why loading everything to the DTO?
        # - very good for the transfer that was the plan
        # - still unsure why not moving all from here to the class?
        extracted_detect = namespace.pop("detect", None)
        extracted_catch = namespace.pop("catch", None)

        cls = super().__new__(mcs, name, bases, namespace, data=data, **kwargs)

        # TODO: check order, why after super().__new__?
        # - maybe insert into dto before?
        if extracted_detect:
            cls._data.detect = extracted_detect
        if extracted_catch:
            cls._data.catch = extracted_catch

        return cls

    def __init__(
        cls,  # noqa:N805
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs,  # TODO: forward? destroy in SstMeta?
    ):

        super().__init__(name, bases, namespace)

        # MOVE: probably FunctorMeta.__new__
        if not hasattr(cls, "_func"):
            # MOVE: maybe new forge.blueprint._defaults
            def default_func(self, *args, **kwargs) -> None:
                raise NotImplementedError("Provide func or override __call__!")

            cls._func: Callable = default_func  # TODO: when parametrize?

        cls.__name__ = clsname(cls)  # LATER: format.inject?
        cls.__qualname__ = cls.__qualname__ or cls.__name__

    def __call__(cls, *args, **kwargs):  # noqa:N805
        """The Hybrid Triple Dispatch (Class-Level)"""

        # IDEA: replace below by ..func._hybrid?

        target = args[0] if args else None

        # CASE 1: Direct Execution -> MyFunctor("data")
        if (
            target is not None
            and cls._data.detect
            and cls._data.detect(target)
        ):
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
            f"Invalid Hybrid Dispatch for {clsname(cls)}. Target: {target}"
        )


if TYPE_CHECKING:
    _cls_meta: type[Meta] = FunctorMeta
    _cls_data: type[MetaData] = FunctorMetaData
    _instance_data: MetaData = FunctorMetaData()
