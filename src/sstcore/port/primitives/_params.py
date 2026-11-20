"""
Most basic parts

.
"""

__all__: list[str] = [
    "Var",
    "Args",
    "Kwargs",
    "Params",
    "TupleBase",
]

from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    Sequence,
)
from itertools import combinations
from typing import Any, NamedTuple, Self

from ._field import TupleField
from ._hashed import HashedTuple


class TupleBase:
    __iter__: Any

    sep = TupleField[str](", ")
    # sep: str

    def __str__(self):
        return f"{type(self).__name__}[{self.joined}]"

    @property
    def joined(self) -> str:
        return self.sep.join(f"{x}" for x in self)

    @classmethod
    def mix[T](cls, target: type[T], /) -> type[T]:
        # NOTE: intersection partially works, but probably too many side effects
        # def mix[T](cls, target: type[T], /) -> type[T & Self]:
        """Inject Behaviour into Named Tuples"""
        namespace: dict[str, Any] = {
            "__qualname__": target.__qualname__,
            "__module__": target.__module__,
            "__doc__": target.__doc__,
        }
        return type(target.__name__, (target, cls), namespace)  # ty:ignore

    def __reduce__(self) -> tuple[Any, ...]:
        """Provide anchor for Pickling"""
        raw_fields: tuple[Any, ...] = tuple(tuple.__iter__(self))  # ty:ignore
        if state := getattr(self, "__dict__", None):
            return type(self), raw_fields, state
        return type(self), raw_fields


@TupleBase.mix
class Var[T: Any = Any](NamedTuple):
    name: str
    value: T

    sep = TupleField[str]("=")

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Invoke the Value if callable or provide its Representation"""
        if callable(self.value):
            return self.value(*args, **kwargs)
        return f"Not Callable: {self}[{self.value!r}]"

    def __bool__(self) -> bool:
        return bool(self.value)

    def __getitem__(self, key: str | int) -> Any:  # ty: ignore
        match key:
            case int() as index if index == 0:
                return self.name
            case int() as index if index == 1:
                return self.value
            case int() as index:
                raise IndexError(f"{self} got {index=} but needs [0, 1]")
            case str() if key != (name := self.name):
                raise KeyError(f"{self} got {key=} but needs {name=}")
            case str():
                return self.value
            case _:
                raise TypeError(f"{self}: Unknown {type(key)}[{key=}]")

    def keys(self) -> KeysView[str]:
        return KeysView({self.name: None})

    def hashed(self, strict=True) -> HashedTuple:
        """Recursively Enforce Freeze and Hash (strict=False -> str(obj))"""
        return HashedTuple(*self, strict=strict)

    @classmethod
    def gettr(cls, target: Any, name: str, /) -> Self:
        """Hit the Target with the Name to get the Attr"""
        return cls(name, value=getattr(target, name))


@TupleBase.mix
class Args(NamedTuple):
    """Capture and Visualize Positional Parameter"""

    args: Sequence = ()

    # sep = TupleField[str](", ")
    keyformat = TupleField[Callable[[Any], str]](lambda v: f"{v}")

    def __iter__(self) -> Iterator[object]:  # ty:ignore
        yield from self.args

    def __len__(self) -> int:  # ty:ignore
        return len(self.args)

    def __bool__(self) -> bool:
        return bool(self.args)

    def __getitem__(self, index: int) -> Any:  # ty: ignore
        """Forward Index to inner Tuple"""
        return self.args[index]

    def keys(self):
        # IDEA: mode like index,string,custom keyformat
        # - use for format, maybe for keys/kwargs? but ensure unique!
        # - maybe on Var? define the rules at the lowest node
        return KeysView({i: None for i, _ in enumerate(self)})

    def kwargs(self) -> Kwargs:
        """Transform Sequential Args into Mapped Kwargs"""
        return Kwargs({self.keyformat(v): v for v in self})

    @classmethod
    def absorb(cls, *args) -> Self:
        return cls(args)

    @classmethod
    def slots(cls, target, /) -> Self:
        """Build from __slots__s of Target"""
        return cls(tuple(iter_slots(target)))


def iter_slots(target) -> Iterable[Var]:
    seen: set[str] = set()
    for cls in type(target).__mro__:
        for slot in _get_slot(cls):
            if slot in ("__dict__", "__weakref__"):
                continue
            if slot.startswith("__") and not slot.endswith("__"):
                slot = f"_{cls.__name__.lstrip('_')}{slot}"
            if slot not in seen and hasattr(target, slot):
                seen.add(slot)
                yield Var.gettr(target, slot)


def _get_slot(cls: type) -> Iterable[str]:
    _slots = cls.__dict__.get("__slots__", ())
    return _slots if not isinstance(_slots, str) else (_slots,)


@TupleBase.mix
class Kwargs(NamedTuple):
    """Capture and Visualize Keyword Parameter"""

    kwargs: Mapping[str, Any] = {}  # LATER: frozen or not?

    sep = TupleField[str](", ")

    def __iter__(self) -> Iterator[Var]:  # ty:ignore
        # IDEA: lock this down? avoid accidental usage as Args
        for name, value in self.kwargs.items():
            yield Var(name, value)

    def __len__(self) -> int:  # ty:ignore
        return len(self.kwargs)

    def __bool__(self) -> bool:
        return bool(self.kwargs)

    def __getitem__(self, key: str | int) -> Any:  # ty: ignore
        if isinstance(key, int):
            return self[tuple(self.keys())[key]]
        return self.kwargs[key]

    def keys(self) -> KeysView[str]:
        return self.kwargs.keys()

    def args(self) -> Args:
        """Transform Mapped Kwargs into Sequential Args"""
        return Args.absorb(*(Var(name, value) for name, value in self))

    @classmethod
    def absorb(cls, **kwargs) -> Self:
        return cls(kwargs)

    @classmethod
    def vars(cls, target, /, *, live_view=False) -> Self:
        """Build from vars of Target - direct reference with live_view"""
        return cls(kwargs=vars(target) if live_view else dict(vars(target)))


@TupleBase.mix
class Params(NamedTuple):
    """Capture and Visualize 1 Signature"""

    args: Args = Args()
    kwargs: Kwargs = Kwargs()

    sep = TupleField[str](", ")

    def __str__(self):
        return f"{type(self).__name__}[{self.args}{self.sep}{self.kwargs}]"

    def __bool__(self) -> bool:
        return bool(self.args) or bool(self.kwargs)

    def __iter__(self) -> Iterator[Any]:
        yield from self.args

    def __getitem__(self, key: str) -> Any:  # ty: ignore
        return self.kwargs[key]

    def keys(self) -> KeysView[str]:
        return self.kwargs.keys()

    def feed[R](self, func: Callable[..., R], /) -> R:
        """Apply captured *args,**kwargs to Function"""
        return func(*self, **self)

    @classmethod
    def absorb(cls, *args, **kwargs) -> Self:
        return cls(Args(args), Kwargs(kwargs))


#
if __name__ == "__main__":

    def main():
        _all()
        _var()
        # _args()
        # _args_kwargs()
        # _param()
        # _feeding()
        pass

    from rich import print
    from rich.panel import Panel
    from rich.text import Text

    def _str(text, /, prefix=True):
        return Text(f"{'str: ' if prefix else ''}{text}")

    def _panel(text, style="cyan", /):
        print(Panel(Text(f"{text}"), style=style))

    def _full(x):
        _panel(repr(x), "green")
        print(f"{len(x)=}")
        print("raw", x)
        print(_str(x))
        print("repr", repr(x))
        for i, y in enumerate(x):
            print(f"item[{i}]", y)

    def _deref(param):
        _panel(f"Start of deref for {param}")
        print(*param)
        print({**param})
        print(*param, {**param})

    def _args():
        args = Args.absorb("ss", 5, {"hello", "set"})
        _full(args)
        print(args.keys())
        for k in args.keys():
            print(args[k])
        _deref(args)

    var1 = Var("name", 5)
    var2 = Var("other", 20)

    def _var():
        _full(var1)
        _full(var2)
        _panel({**var1, **var2}, "yellow")
        for x in (var1, var2):
            _full(x)
        var1.sep = ":::::"
        for x in (var1, var2):
            _full(x)

    arg1 = Args()
    arg2 = Args.absorb("ss", 5, {"hello", "set"})
    kwarg1 = Kwargs()
    kwarg2 = Kwargs({"a": 1, "b": 2, "c": 3, "d": 4})

    def _args_kwargs():
        _panel("Single", "gold3")
        for x in (arg1, arg2, kwarg1, kwarg2):
            _full(x)

    def _param():
        _panel("combinations", "gold3")
        for a, k in combinations((arg1, arg2, kwarg1, kwarg2), 2):
            _panel(p := Params(a, k))  # ty:ignore
            _full(p)
            _deref(p)

    def _dip(header, text, color="yellow") -> Panel:
        return Panel(f"{header} [{color}]{text}[/]", style="cyan")

    param = Params.absorb("Start", "main text", color="green")

    def _all():
        _full(var2)
        _full(arg2)
        _full(kwarg2)
        _full(param)

    def _feeding():
        print(param)
        dipped = param.feed(_dip)
        # reveal_type(dipped)
        print(dipped)

    main()
