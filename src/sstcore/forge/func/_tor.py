"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

__all__: list[str] = [
    "BaseFunctor",
]

from collections.abc import Callable
from typing import Any, Self, TypeGuard, Unpack, reveal_type

from loguru import logger

from ...brick.field import StrategyField
from ...brick.reflect import clsname, funcname
from ...port import functorial
from ...port.event.emit import BoundLog
from ...port.event.name import CoreEvent
from ...port.link import portlink
from ..engine import FunctorMeta
from ._zero import FunctorInput, FunctorMetaInput, FunctorSpec, FunctorView


@portlink(functorial.Functorial)  # LATER: who is Functor?
class BaseFunctor[**Args, Result](
    FunctorView, metaclass=FunctorMeta, data=FunctorMetaInput
):
    """Ensure Requirements and close MRO forwarding"""

    # if TYPE_CHECKING:
    #     _emit: BoundLog

    def __init__(self, **kwargs: Unpack[FunctorInput[Args, Result]]):
        _spec = FunctorSpec.absorb(kwargs)

        self._assign_name(_spec.name)

        if _spec.call is not None:
            self._call: Callable[Args, Result] = _spec.call

        if _spec.emit is not None:
            self._emit: BoundLog = _spec.emit  # LATER: emitter?

        if kwargs:
            self._emit(f"Undestroyed kwargs: {kwargs!r}")

        super().__init__()

    def _assign_name(self, name: str = ""):
        _name: str = self._format_name(name)
        self.__name__: str = _name
        self.__qualname__: str = _name

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


if __name__ == "__main__":
    reveal_type(BaseFunctor._emit)
    x: BoundLog = BaseFunctor._emit

    def is_valid_emit(fn: Any) -> TypeGuard[BoundLog]:
        """Validation logic follows later..."""
        return True

    if is_valid_emit(BaseFunctor._emit):
        reveal_type(BaseFunctor._emit)
        y: BoundLog = BaseFunctor._emit

    _functor = BaseFunctor(name="TestFunctor")
    reveal_type(_functor._emit)
    _functor._emit("Hello", level="DEBUG", test=33)
    try:
        _functor._emit("this", "should", "fail", "fast")
    except TypeError as error:
        print(f"{error=}")

    def new_emit(message: str, /, **_):
        # FIX: self? how to add this?
        print(message)

    _functor._emit = new_emit
    reveal_type(_functor._emit)
    _functor._emit("Hello", test=33)
    try:
        _functor._emit("this", "should", "fail", "fast")
    except TypeError as error:
        print(f"{error=}")

    if is_valid_emit(_functor._emit):
        reveal_type(_functor._emit)
        _functor._emit("Hello", level="DEBUG", test=33)
        try:
            _functor._emit("this", "should", "fail", "fast")
        except TypeError as error:
            print(f"{error=}")
