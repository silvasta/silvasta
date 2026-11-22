"""
Most basic parts

.
"""

__all__: list[str] = [
    "Var",
    "Args",
    "KeyFormatting",
    "Kwargs",
    "VarsView",
    "Params",
    "TupleBase",
]

import collections.abc as _cabc
import typing as _typing
from collections.abc import Callable
from typing import Any, Self

from ._field import TupleField
from ._frozen import frozendict
from ._hashed import HashedTuple


class KeyFormatting(_typing.Protocol):
    # IDEA: mode like index,string,custom keyformat
    # - use for format, maybe for keys/kwargs? but ensure unique!
    # - maybe on Var? define the rules at the lowest node
    def __call__(self, target: object, /) -> str:
        """Render the Value to a valid Key"""


# LATER: decide who holds vars/slots or both for all
type VarsView = _typing.Literal["live", "dict", "frozen"]


class TupleBase:
    __iter__: Any
    sep = TupleField[str](", ")

    def __str__(self):
        return f"{type(self).__name__}[{self.joined}]"

    @property
    def joined(self) -> str:
        """Concat all items in joins that needs to be joined"""
        return self.sep.join(f"{x}" for x in self.joins())

    def joins(self) -> _cabc.Iterator:
        """Stream the visual representation joins (indepenent of __iter__)"""
        yield from self

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
class Var[T: Any = Any](_typing.NamedTuple):
    name: str
    value: T

    sep = TupleField[str]("=")

    def __call__(self, *args, **kwargs) -> Any:
        """Invoke the Value if callable or provide its Representation"""
        if callable(self.value):
            return self.value(*args, **kwargs)
        return f"Not Callable: {self}[{self.value!r}]"

    def __bool__(self) -> bool:
        return bool(self.value)

    def __getitem__(self, key: str | int) -> T | str:  # ty: ignore
        """Hardcore Encode Default Behaviour plus Var()[name]=value access"""
        if _typing.TYPE_CHECKING:
            key: Any = key
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

    def keys(self) -> _cabc.KeysView[str]:
        return _cabc.KeysView({self.name: None})

    def hashed(self, strict: bool = True) -> HashedTuple:
        """Recursively Enforce Freeze and Hash (strict=False -> str(obj))"""
        return HashedTuple(*self, strict=strict)

    @classmethod
    def gettr(cls, target: object, name: str, /) -> Self:
        """Hit the Target with the Name to get the Attr"""
        return cls(name, value=getattr(target, name))


@TupleBase.mix
class Args(_typing.NamedTuple):
    """Capture and Visualize Positional Parameter"""

    args: _cabc.Sequence = ()

    sep = TupleField[str](", ")
    keyformat = TupleField[KeyFormatting](lambda v: f"{v}")

    def __iter__(self) -> _cabc.Iterator[object]:  # ty:ignore
        yield from self.args

    def __len__(self) -> int:  # ty:ignore
        return len(self.args)

    def __bool__(self) -> bool:
        return bool(self.args)

    def __getitem__(self, index: int) -> Any:  # ty: ignore
        """Forward Index to inner Tuple"""
        return self.args[index]

    def keys(self):
        return _cabc.KeysView({i: None for i, _ in enumerate(self)})

    def kwargs(self) -> Kwargs:
        """Transform Sequential Args into Mapped Kwargs"""
        return Kwargs({self.keyformat(v): v for v in self})

    @classmethod
    def absorb(cls, *args) -> Self:
        return cls(args)

    @classmethod
    def slots(cls, target: object, /) -> Self:
        """Build from __slots__ of Target"""
        return cls(args=tuple(iter_slots(target)))


def iter_slots(target: object) -> _cabc.Iterable[Var]:
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


def _get_slot(cls: type) -> _cabc.Iterable[str]:
    _slots = cls.__dict__.get("__slots__", ())
    return _slots if not isinstance(_slots, str) else (_slots,)


@TupleBase.mix
class Kwargs(_typing.NamedTuple):
    """Capture and Visualize Keyword Parameter"""

    kwargs: _cabc.Mapping[str, Any] = {}  # LATER: frozen or not?

    sep = TupleField[str](", ")

    def __iter__(self) -> _cabc.Iterator[Var]:  # ty:ignore
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

    def keys(self) -> _cabc.KeysView[str]:
        return self.kwargs.keys()

    def args(self) -> Args:
        """Transform Mapped Kwargs into Sequential Args"""
        return Args.absorb(*(Var(name, value) for name, value in self))

    @classmethod
    def absorb(cls, **kwargs) -> Self:
        return cls(kwargs)

    @classmethod
    def vars(cls, target, /, *, view: VarsView = "dict") -> Self:
        """Build from vars of Target - direct reference with live_view"""
        match view:
            case "live":
                return cls(kwargs=vars(target))
            case "dict":
                return cls(kwargs=dict(vars(target)))
            case "frozen":
                return cls(kwargs=frozendict(vars(target)))


@TupleBase.mix
class Params(_typing.NamedTuple):
    """Capture and Visualize 1 Signature"""

    args: Args = Args()
    kwargs: Kwargs = Kwargs()

    sep = TupleField[str](", ")

    def __str__(self):
        return f"{type(self).__name__}[{self.args}{self.sep}{self.kwargs}]"

    def __bool__(self) -> bool:
        return bool(self.args) or bool(self.kwargs)

    def joins(self) -> _cabc.Iterator:  # TEST:
        yield from self.args
        yield from self.kwargs

    def __iter__(self) -> _cabc.Iterator[Any]:
        yield from self.args

    def __getitem__(self, key: str) -> Any:  # ty: ignore
        return self.kwargs[key]

    def keys(self) -> _cabc.KeysView[str]:
        return self.kwargs.keys()

    def feed[R](self, func: Callable[..., R], /) -> R:
        """Apply captured *args,**kwargs to Function"""
        return func(*self, **self)

    @classmethod
    def absorb(cls, *args, **kwargs) -> Self:
        return cls(Args(args), Kwargs(kwargs))
