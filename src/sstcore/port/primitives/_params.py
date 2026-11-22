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

from ..empty import MayNot
from ._field import TupleField
from ._frozen import frozendict
from ._hashed import HashedTuple

# AI_TASK: Access to members:
# - Args() or Kwargs() should build without a default (other members as well)
# - so far args.args or kwargs.kwargs was fine, still it could be improved
# - quick conversion presets:
#  - already installed are arg_tuple and kwarg_dict on Params
#  - something like this could be established everywhere
#  - Ideas: args.tuple, args.list, args.set, kwargs.frozendict, kwargs.dict
#  - probably difficult because of the naming conflict with builtins...
#  - if possible, short names, 1 word names, something that can be stacked:
#    - Params.arg_tuple might be replaced by Params.args.tuple
#    - instead of combined words, just dot-get it one layer deeper
#    - Ideas: Params.kwargs.frozen or Params.kwargs.as_dict or Params.args.hashed

# AI_TASK: unified strategy for methods:
# - create: method to avoid inserting empty defaults
#   - concept needed that works fast and efficeant not only for here,
#     but for other locations like RaiserParams or andy other new setup
#   - for Var at minimum the name, probably better both args are required
#   - maybe with __init__ or __new__? (after subclassing the fixed members class)
#   - possible to encode in TupleBase? (including proper typing)
# - absorb: swallow the dereferenced params, proved already very helpful
#   - so far fine, maybe ideas how to forward this to classes that hold params
# - vars/slots: fine so far, maybe future ideas how to make them better availabel

# AI_TASK: Rendering:
# - Something like this for each member: icon = TupleField[str]("X")
# - used inside the brackets [X|name=...] (first position with rich.print != a..z)
# - for stacked ones like Kwargs it sometimes helps when each variable is clearly separated like  Var[name=value],...
#   depending on the visualization setup this can as well be polluting, ideas how to make this configurable?
# - Soon I want to build some other NamedTuples that handle small pieces of Data
#   - one of them is for collecting and formatting help-messages
#   - some rendering core controlled by TupleBase and precisely injected will help
# - I assume __format__ can help here, even injected to all, allowing still for only that rendering that is desired


class TupleBase:
    """Inject Behaviour into NamedTuples"""

    __iter__: Any
    sep = TupleField[str](", ")

    def __str__(self):
        return f"{type(self).__name__}[-{self.joined}]"

    @property
    def joined(self) -> str:
        """Concat all items in joins that needs to be joined"""
        return self.sep.join(f"{x}" for x in self.joins())

    def joins(self) -> _cabc.Iterator:
        """Stream the visual representation joins (indepenent of __iter__)"""
        yield from self

    @classmethod
    def mix[T](cls, target: type[T], /) -> type[T]:
        # PARAM: toggle that sometimes helps and sometimes not
        # def mix[T](cls, target: type[T], /) -> type[T & Self]:  # ty:ignore
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


class KeyFormatting(_typing.Protocol):
    # IDEA: mode like index,string,custom keyformat
    # - use for format, maybe for keys/kwargs? but ensure unique!
    # - maybe on Var? define the rules at the lowest node
    def __call__(self, target: object, /) -> str:
        """Render the Value to a valid Key"""


# LATER: decide who holds vars/slots or both for all
type VarsView = _typing.Literal["live", "dict", "frozen"]


@TupleBase.mix
class Var[T: Any = Any](_typing.NamedTuple):
    name: str
    value: T

    sep = TupleField[str]("=")

    # IDEA: render attributes depending on their type!
    # - like for functions the name, or for types, maybe hasattr(x,__name__)

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
    def create(cls, args: MayNot[_cabc.Sequence | Args] = None) -> Self:
        return args if isinstance(args, cls) else cls(args or ())

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

    kwargs: _cabc.Mapping[str, Any]  # = {}  # LATER: frozen or not?

    sep = TupleField[str](", ")

    def __iter__(self) -> _cabc.Iterator[Var]:  # ty:ignore
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
    def create(
        cls, kwargs: MayNot[_cabc.Mapping[str, Any] | Kwargs] = None
    ) -> Self:
        return (
            kwargs
            if isinstance(kwargs, cls)
            else cls(kwargs=kwargs if isinstance(kwargs, _cabc.Mapping) else {})
        )

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

    args: Args
    kwargs: Kwargs

    sep = TupleField[str](", ")

    @property
    def arg_tuple(self) -> tuple[Any, ...]:
        return tuple(self.args.args)

    @property
    def kwarg_dict(self) -> dict[str, Any]:
        return dict(self.kwargs.kwargs)

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

    @classmethod
    def create(
        cls,
        args: MayNot[_cabc.Sequence | Args] = None,
        kwargs: MayNot[_cabc.Mapping | Kwargs] = None,
    ) -> Self:
        return cls(args=Args.create(args), kwargs=Kwargs.create(kwargs))
