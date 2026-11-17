"""
Most basic parts

.
"""

from itertools import combinations

__all__: list[str] = [
    "Var",
    "Args",
    "Kwargs",
    "Params",
]

from collections.abc import Iterable, Iterator, KeysView, Mapping, Sequence
from typing import Any, NamedTuple, Self

from ._field import TupleField


class BaseControl:
    # inner = TupleField[str]("=")
    # outer = TupleField[str](", ")
    __iter__: Any
    outer: str
    inner: str

    def __str__(self):
        return f"{type(self).__name__}[{self.data()}]"

    # def __tokens__(self) -> Iterator[Any]:
    #     """
    #     Yield items for view rendering.
    #
    #     Defaults to iterating over `self`, filtering out empty subsections.
    #     """
    #     for x in self:  # ty:ignore
    #         if x is not None and x != () and x != {}:
    #             yield x

    def data(self) -> str:
        # return self.outer.join(self.item(x) for x in self.__tokens__())
        return self.outer.join(self.item(x) for x in self)

    def item(self, entry) -> str:
        is_kwarg: bool = (
            isinstance(entry, tuple)
            and not isinstance(entry, BaseControl)
            and len(entry) == 2
        )
        return f"{entry[0]}{self.inner}{entry[1]}" if is_kwarg else f"{entry}"

    @classmethod
    def mix[T](cls: type[Self], target: type[T]) -> type[T & Self]:  # ty:ignore
        namespace = {
            "__qualname__": target.__qualname__,
            "__module__": target.__module__,
            "__doc__": target.__doc__,
        }
        return type(target.__name__, (target, cls), namespace)  # ty:ignore


@BaseControl.mix
class Var(NamedTuple):
    name: str
    value: Any

    # inner = TupleField[str]("=")
    outer = TupleField[str]("=")  # AI: somehow here the outer is needed...

    @classmethod
    def gettr(cls, target: Any, name: str, /) -> Self:
        """Hit the Target with the Name to get the Attr"""
        return cls(name, value=getattr(target, name))

    # def __tokens__(self) -> Iterator[tuple[str, Any]]:
    #     # CHECK: what is the difference to (unchange) Self.__iter__??
    #     """Yield a single (name, value) tuple for `base.item` to format."""
    #     yield (self.name, self.value)

    def keys(self) -> KeysView[str]:
        return {self.name: None}.keys()

    def __getitem__(self, key: str) -> Any:  # ty: ignore
        if key == (name := self.name):
            return self.value
        raise KeyError(f"Got {name=} but need {key=} for value[{self.value}]")

    def __bool__(self) -> bool:
        return bool(self.value)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Invoke the Value if callable or provide its Representation"""
        if callable(self.value):
            return self.value(*args, **kwargs)
        return f"Not Callable: {self}[{self.value!r}]"


@BaseControl.mix
class Args(NamedTuple):
    args: Sequence = ()

    # inner = TupleField[str]("=")
    outer = TupleField[str](", ")

    def __iter__(self) -> Iterator[object]:  # ty:ignore
        yield from self.args

    def __bool__(self) -> bool:
        return bool(self.args)

    def kwargs(self) -> Kwargs:
        """Transform Sequential Args into Mapped Kwargs"""
        return Kwargs.absorb(*(Var(f"{v}", v) for v in self))

    @classmethod
    def absorb(cls, *args) -> Self:
        return cls(args)


@BaseControl.mix
class Kwargs(NamedTuple):
    kwargs: Mapping[str, Any] = {}

    inner = TupleField[str]("=")
    outer = TupleField[str](", ")

    def __iter__(self) -> Iterator[Var]:
        for name, value in self.kwargs.items():
            yield Var(name, value)

    def __bool__(self) -> bool:
        return bool(self.kwargs)

    def keys(self) -> KeysView[str]:
        return self.kwargs.keys()

    def __getitem__(self, key: str) -> Any:  # ty: ignore
        return self.kwargs[key]

    @classmethod
    def vars(cls, target, /) -> Self:
        """Build from vars of Target"""
        return cls(kwargs=vars(target).items())

    def args(self) -> Args:
        """Transform Mapped Kwargs into Sequential Args"""
        return Args.absorb(*(Var(name, value) for name, value in self))

    @classmethod
    def absorb(cls, *args: Var | Iterable[Var], **kwargs) -> Self:
        """Accept multiple `Var` instances, an iterable of `Var`s, or raw **kwargs."""
        merged: dict[str, Any] = {}
        for arg in args:
            if isinstance(arg, Var):
                merged[arg.name] = arg.value
            elif isinstance(arg, Iterable):
                for v in arg:
                    merged[v.name] = v.value
        merged.update(kwargs)
        return cls(merged)


@BaseControl.mix
class Params(NamedTuple):
    """Capture and Visualize 1 Signature"""

    inner = TupleField[str]("=")
    outer = TupleField[str](", ")

    args: Args = Args()
    kwargs: Kwargs = Kwargs()

    @classmethod
    def absorb(cls, *args, **kwargs) -> Self:
        return cls(Args.absorb(*args), Kwargs.absorb(**kwargs))

    def __iter__(self) -> Iterator[Any]:
        yield from self.args

    def keys(self) -> KeysView[str]:
        return self.kwargs.keys()

    def __getitem__(self, key: str) -> Any:  # ty: ignore
        return self.kwargs[key]


#
if __name__ == "__main__":
    from rich import print as print
    from rich.panel import Panel
    from rich.text import Text

    def _p(*args, **kwargs):
        if args:
            first, *rest = args
            args = Text(str(first)), *rest
        print(*args, **kwargs)

    def _panel(text, style="cyan", /):
        print(Panel(Text(f"{text}"), style=style))

    def _deref(param):
        _panel(f"Start of Deref for {param}")
        print(*kw)
        print({**kw})
        print(*kw, {**kw})

    def _full(x):
        _panel(str(x))
        _p(str(x))
        _p(repr(x))
        for y in x:
            print(y)

    def connect(host: str, port: int, timeout: float = 5.0):
        return f"{host}:{port} ({timeout}s)"

    kw = Kwargs.absorb(host="localhost", port=8080)

    print(connect(**kw))

    config = {"timeout": 10.0, **kw, "port": 9090}
    print(config)

    _panel(kw)
    _deref(kw)

    var1 = Var("name", 5)
    var2 = Var("other", 20)
    _panel({**var1, **var2})

    for x in (var1, var2):
        _full(x)

    var1.outer = ":::::"

    for x in (var1, var2):
        _full(x)

    arg1 = Args()
    arg2 = Args.absorb("ss", 5, {"hello", "set"})
    kwarg1 = Kwargs()
    kwarg2 = Kwargs({"a": 1, "b": 2, "c": 3})

    for x in (arg1, arg2, kwarg1, kwarg2):
        _panel(str(x), "blue")
        _p(str(x))
        _p(repr(x))
        for y in x:
            print(y)

    for a, k in combinations((arg1, arg2, kwarg1, kwarg2), 2):
        _panel(p := Params(a, k))
        _full(p)
        _deref(p)
