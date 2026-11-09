"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

__all__: list[str] = [
    "BaseFunctor",
]

from collections.abc import Callable
from typing import Any, Self, Unpack

from loguru import logger

from ...brick.field import StrategyField
from ...brick.reflect import clsname, funcname
from ...port import functorial
from ...port.event.name import CoreEvent
from ...port.link import portlink
from ..engine import FunctorMeta
from ._zero import FunctorInput, FunctorMetaInput, FunctorSpec, FunctorView


@portlink(functorial.Functorial)  # LATER: who is Functor?
class BaseFunctor[**Args, Result](
    FunctorView, metaclass=FunctorMeta, data=FunctorMetaInput
):
    """Ensure Requirements and close MRO forwarding"""

    def __init__(self, **kwargs: Unpack[FunctorInput[Args, Result]]):

        _spec = FunctorSpec.absorb(kwargs)

        name: str = self._format_name(_spec.name)
        self.__name__: str = name
        self.__qualname__: str = name

        if _spec.call is not None:
            self._call: Callable[Args, Result] = _spec.call
        if _spec.emit is not None:
            self._emit: Callable = _spec.emit  # LATER: emitter?

        if kwargs:
            self._emit(f"Undestroyed kwargs: {kwargs!r}")

        super().__init__()

    def _format_name(self, name: str = "") -> str:
        """Prepare Name if empty or by critera defined in Subhook"""
        return name or funcname(self._call, default=f"{clsname(self)}Unit")

    @classmethod
    def __mount__(cls, _host: Any, /, *, name: str = "", **kwargs: Any) -> Self:
        return cls(name=name, **kwargs)

    def __call__(self, *args: Args.args, **kwargs: Args.kwargs) -> Result:
        return self._call(*args, **kwargs)

    @StrategyField(bind_to_self=True)
    def _call(self, *args: Args.args, **kwargs: Args.kwargs):
        raise AttributeError(f"{self} has no _call!", self, args, kwargs)

    @StrategyField(bind_to_self=True)
    def _emit(self, message: str, /, *, level: str = "ERROR", **extra) -> None:
        logger.bind(
            event_name=CoreEvent.FUNCTOR, sender=f"{self}", **extra
        ).log(level.upper(), message)
