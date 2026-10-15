"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

__all__: list[str] = [
    "BaseFunctor",
]


from collections.abc import Callable

from loguru import logger

from ...brick.field import MorphingField, StrategyField
from ...brick.reflect import clsname, funcname
from ...port import functorial
from ...port.link import portlink
from ..engine import FunctorMeta, FunctorMetaData

FunctorInput = FunctorMetaData()


@portlink(functorial.Functorial)  # RENAME: who is Functor?
class BaseFunctor[**Args, Result](metaclass=FunctorMeta, data=FunctorInput):
    """Ensure Requirements and close MRO forwarding"""

    def __init__(
        self,
        call: Callable[Args, Result] | None = None,
        name: str = "",
        **kwargs,
    ):  # LATER: __init_subclass__ from here?

        if call is not None:
            self.call: Callable[Args, Result] = call

        name: str = name or funcname(self.call, default=f"{clsname(self)}Unit")
        self.__name__: str = name
        self.__qualname__: str = name

        if kwargs:
            self.emit(f"Undestroyed kwargs: {kwargs!r}")

        super().__init__()

    def __call__(self, *args: Args.args, **kwargs: Args.kwargs) -> Result:
        return self.call(*args, **kwargs)

    @StrategyField(bind_to_self=True)
    def call(self, *args, **kwargs):
        raise AttributeError(
            "Functor is Missing: [ _call_ ]!", self, args, kwargs
        )

    @MorphingField(bind_to_self=True)
    def emit(self, *args, **kwargs) -> None:  # MOVE: global meta defaults
        logger.debug(*args, sender=str(self), **kwargs)
