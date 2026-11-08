"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

__all__: list[str] = [
    "BaseFunctor",
]

from collections.abc import Callable
from typing import Any, Self, Unpack

from ...brick.field import MorphingField, StrategyField
from ...brick.reflect import clsname, funcname
from ...port import functorial
from ...port.link import portlink
from ..engine import FunctorMeta
from ._zero import FunctorMetaInput, FunctorView


@portlink(functorial.Functorial)  # LATER: who is Functor?
class BaseFunctor[**Args, Result](
    FunctorView, metaclass=FunctorMeta, data=FunctorMetaInput
):  # LATER: __init_subclass__ with registry from here?
    """Ensure Requirements and close MRO forwarding"""

    def __init__(self, **kwargs: Unpack[FunctorInput[Args, Result]]):
        spec: FunctorSpec[Args, Result] = FunctorSpec.absorb(kwargs)

        name: str = self._format_name(spec.name)
        self.__name__: str = name
        self.__qualname__: str = name

        if spec.call is not None:
            self._call: Callable[Args, Result] = spec.call

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

    @MorphingField(bind_to_self=True)  # MOVE: to meta defaults when improved
    def _emit(
        self,
        *args,
        level: str = "DEBUG",
        exception: BaseException | None = None,
        **kwargs,
    ) -> None:
        if getattr(self, "debug", False):
            from rich import print

            print(*args, **kwargs)
            return

        from loguru import logger

        logger.opt(exception=exception).log(
            level, *args, sender=str(self), **kwargs
        )


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FunctorView:
    # CHECK: _data: FunctorMetaData

    def __str__(self) -> str:
        return f"[({reflect.clsname(self)})][{reflect.name(self)}]"

    def __repr__(self) -> str:
        return f"{self}({norm.dict_to_str(vars(self))})"

    #  LINE: -- Select, later on -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __rich__(self) -> str:
        return f"{reflect.clsname(self)}[{reflect.name(self)}]"

    def __rich1__(self) -> Richable:
        return colors(reflect.clsname(self), self._data.color)

    def __rich2__(self) -> Richable:
        return colorize.modules(self)
