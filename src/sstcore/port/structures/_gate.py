"""
Govern the Behaviour of tiny helper Mappings

- MapGate: shared base with utils and rules
- LazyMap: delay loading until imports are safe and loader ready
- ActiveMap: grow at any time usually by inserted key and values
- CacheGate: flyweight fetch with hit accounting and a FIFO cap

"""

__all__: list[str] = [
    "MapGate",
    "LazyMap",
    "CacheGate",
    "is_nullary",
    "LoadMode",
    "Fallback",
    "GateRaiser",
]


from collections.abc import Callable, Hashable, Iterator, KeysView, Mapping
from contextlib import contextmanager
from enum import Enum, auto
from inspect import Parameter, signature
from typing import Any, ClassVar, Literal, Self, Unpack
from typing import Unpack as _U  # noqa: N814

from .. import _error as _err
from .._types import _Stringable
from ..empty import VOID, MayBe, MayNot
from ..primitives import Args, Kwargs, Var
from ._loader import Loader, Loading

type LoadMode = Literal["auto", "item", "table"]
type Fallback[K, V] = Callable[[K], V] | Loader[[K], V]


class MapGate[K: Hashable, V]:
    """Prepare the Structure for the Gating Mappings"""

    def __init__(self, data: Mapping[K, V] | None = None):
        self._data: dict[K, V] = {}
        if data:
            self.absorb(data)

    def __getitem__(self, key: object, /) -> V:
        """Read Value or call Missing and Raise on Fail"""

        lock: K = self.locksmith(key)

        if lock in self._data:
            return self._data[lock]

        recovery: MayBe[V] = self.__missing__(lock)

        if recovery is VOID:
            raise GateRaiser.key_miss(key, self)

        return recovery

    def __missing__(self, _lock: K, /) -> MayBe[V]:
        """Find a solution for an absent Key or return VOID to Raise"""
        return VOID

    def __setitem__(self, key: object, value: Any) -> None:
        """Sanitize Inputs, write Value or handle merge result on duplication"""

        lock: K = self.locksmith(key)
        data: V = self.refine(value)

        if lock not in self._data:
            self._data[lock] = data
            return

        resolved: MayBe[V] = self.__merging__(lock, data)

        if resolved is not VOID:
            self._data[lock] = resolved

    def __merging__(self, _lock: K, data: MayBe[V] = VOID, /) -> MayBe[V]:
        """Find a solution for a duplicated Key or return VOID to Ignore"""
        return data

    def __delitem__(self, key: Any) -> None:
        lock: K = self.locksmith(key)
        if lock not in self._data:
            raise GateRaiser.key_miss(key, self)
        del self._data[lock]

    def __contains__(self, key: Any) -> bool:
        """Is the processed Key in Data?"""
        with self.safe():
            if self.locksmith(key) in self._data:
                return True  # type check mock
        return False

    def locksmith(self, key: Any) -> K:
        """Prepare the incoming Key"""
        return key

    def refine(self, value: Any) -> V:
        """Prepare the incoming Value"""
        return value

    @contextmanager
    def safe(self):
        try:
            yield
        except KeyError, TypeError:
            pass

    def absorb(self, map: Mapping | None = None, /, **kwargs) -> Any:
        """Send mapped Items trough register pipeline"""
        if map is not None:
            for key, item in map.items():
                self[key] = item
        for key, item in kwargs.items():
            self[key] = item
        return self

    def get(self, key: Any, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError, TypeError:
            return default

    def clear(self) -> None:
        self._data.clear()

    def keys(self) -> KeysView:
        """Provide Keys for **unpacking"""
        return self._data.keys()

    def values(self) -> Iterator[V]:
        """Stream all Values"""
        yield from self._data.values()

    def items(self) -> Iterator[tuple[K, V]]:
        yield from self._data.items()

    def __iter__(self) -> Iterator[Var]:
        """Provide all named key and value tuples."""
        for name, value in self._data.items():
            var = Var(f"{name}", value)  # LATER: use Var.unique
            var.sep = "::"
            yield var

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return f"{type(self).__name__}[{len(self)}]"

    def __repr__(self) -> str:
        return f"{self}[\n{Kwargs({str(k): v for k, v in self.items()}):nv}\n]"


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LazyMap[K: Hashable, V](MapGate[K, V]):
    """Loader may be for all keys or only for incoming"""

    def __init__(
        self,
        loader: MayNot[Loading[..., Any]] = None,
        /,
        *,
        source: MayNot[Loading[[], Mapping[Any, V]]] = None,
        fallback: MayNot[Loading[[K], V]] = None,
        mode: LoadMode = "auto",
        cache_fallback: bool = True,
        data: Mapping[K, V] | None = None,
        **tkw: Unpack[Loader.Input[V]],
    ) -> None:
        super().__init__(data)
        if mode not in ("auto", "item", "table"):
            raise GateRaiser.load_mode(mode, self)

        item_loader: MayNot[Loading[[K], V]] = fallback

        if loader is not None:
            _raw_fn = loader._func if isinstance(loader, Loader) else loader
            is_table: bool = mode == "table" or (
                mode == "auto"
                and source is None
                and fallback is None
                and is_nullary(_raw_fn)
            )
            if is_table and source is None:
                source: Loader.Func = loader
            elif item_loader is None:
                item_loader: Loader.Func = loader

        self.source: Loader[[], Mapping[Any, V]] = Loader.loading(source)
        self.fallback: Loader[[K], V] = Loader.loading(item_loader, **tkw)
        self.cache_fallback: bool = cache_fallback
        self._mode: LoadMode = mode

    @property
    def is_loaded(self) -> bool:
        """True once no bulk source is pending and data or item loader exists"""
        source_done: bool = not self.source.is_ready or bool(self.source)
        data_available: bool = bool(self._data) or self.fallback.is_ready
        return source_done and data_available

    def hydrate(self) -> Self:
        """Execute bulk table source once and absorb items through pipeline"""
        if self.source.is_pending:
            loaded: MayBe[Mapping[Any, V]] = self.source.load()
            if loaded is not VOID:
                if not isinstance(loaded, Mapping):
                    raise GateRaiser.source_type(self, type(loaded).__name__)
                self.absorb(loaded)
        return self

    def __missing__(self, lock: K, /) -> MayBe[V]:
        """Hydrate pending bulk source first, then resolve via item loader"""
        if self.source.is_pending:
            self.hydrate()
            if lock in self._data:
                return self._data[lock]

        if self.fallback.is_ready:
            self.fallback.reset()
            value: MayBe[V] = self.fallback.load(lock)
            if value is not VOID:
                refined: V = self.refine(value)
                if self.cache_fallback:
                    self._data[lock] = refined
                return refined

        return VOID


def is_nullary(func: Callable[..., Any] | None, /) -> bool:
    """Can this Function be called without any Arguments?"""
    if func is None:
        return False
    try:
        _params = signature(func).parameters.values()
    except TypeError, ValueError:
        return False
    return not any(
        param.kind
        in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
        and param.default is Parameter.empty
        for param in _params
    )


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CacheGate[K: Hashable, V](MapGate[K, V]):
    """Observable Flyweight Cache Gate with hit/miss tracking and size guard."""

    _all_caches: ClassVar[list[CacheGate[Any, Any]]] = []

    def __init__(
        self,
        owner: type[V] | None = None,
        max_size: int | None = None,
        **tkw: _U[Loader.ClsInput],
    ):
        super().__init__()
        _raw_loader = tkw.pop("loader", None)
        self.owner: type[V] | None = owner
        self.loader: Loader[[K], V] = Loader.loading(_raw_loader, **tkw)
        self.max_size: int | None = max_size
        self.hits: int = 0
        self.misses: int = 0
        self.evictions: int = 0
        self._all_caches.append(self)

    def _evict_if_full(self, lock: K) -> None:
        """Evict oldest inserted key (FIFO) when at capacity for a new key"""
        if (
            lock not in self._data
            and self.max_size is not None
            and self.max_size > 0
            and len(self._data) >= self.max_size
        ):
            self._data.pop(next(iter(self._data)))
            self.evictions += 1

    def __setitem__(self, key: Any, value: Any) -> None:
        if self.max_size is not None and self.max_size <= 0:
            return
        lock: K = self.locksmith(key)
        self._evict_if_full(lock)
        super().__setitem__(lock, value)

    def __getitem__(self, key: Any, /) -> V:
        misses_before: int = self.misses
        value: V = super().__getitem__(key)
        if self.misses == misses_before:
            self.hits += 1
        return value

    def __missing__(self, lock: K, /) -> MayBe[V]:
        self.misses += 1
        if not self.loader.is_ready:
            return VOID
        self.loader.reset()
        value: MayBe[V] = self.loader.load(lock)
        if value is not VOID:
            refined: V = self.refine(value)
            self[lock] = refined
            return refined
        return VOID

    def fetch(self, key: Any, factory: Callable[[], V] | None = None) -> V:
        """Fetch cached value or compute via one-off factory / configured loader"""
        if factory is None:
            return self[key]
        lock: K = self.locksmith(key)
        if lock in self._data:
            self.hits += 1
            return self._data[lock]
        self.misses += 1
        value: V = self.refine(factory())
        self[lock] = value
        return value

    @property
    def hit_rate(self) -> float:
        total: int = self.hits + self.misses
        return (self.hits / total) if total else 0.0

    def reset_stats(self) -> None:
        self.hits = self.misses = self.evictions = 0

    def __str__(self) -> str:
        name: str = type(self).__name__
        owner_label: str = f"{self.owner.__name__}::" if self.owner else ""
        _count: str = f"+{self.hits}|-{self.misses}={self.hits + self.misses}"
        return f"{name}[{owner_label}{_count}::({len(self)})::{self.loader}]"

    def __repr__(self) -> str:
        return f"{Kwargs.vars(self):nv}"

    @classmethod
    def report(cls) -> str:
        return (
            "\n".join(f"{cache}" for cache in cls._all_caches)
            or f"{cls.__name__}[none]"
        )


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _TestEnum(Enum):
    FAILING = auto()


class GateRaiser(metaclass=_err.RaiserMeta):
    """Explain Failures Meaningful"""

    _error = _err.SstPortError

    enum_member = _err.RaiserField[[str, _Stringable]](
        KeyError,
        "{label}: Unknown Enum Member: {member!r}",
        test_input=("LABEL", _TestEnum.FAILING),
    )
    enum_type = _err.RaiserField[[str, _Stringable, _Stringable]](
        TypeError,
        "{label}: Expected {owner} but received {incoming}",
        test_input=("LABEL", _TestEnum, Enum),
    )
    enum_extra = _err.RaiserField[[str, _Stringable]](
        KeyError,
        "{label}: Unexpected extra Enum Member(s): {extra}",
        test_input=("LABEL", "EXTRA_MEMBER"),
    )
    enum_missing = _err.RaiserField[[str, _Stringable]](
        KeyError,
        "{label}: Missing value(s) for Enum Member(s): {missing}",
        test_input=("LABEL", "MISSING_MEMBER"),
    )
    key_miss = _err.RaiserField[[_Stringable, _Stringable]](
        KeyError,
        "Invalid {key!r} for {self}!",
        test_input=(423, Loader(default="data")),
    )
    load_mode = _err.RaiserField[[_Stringable, _Stringable]](
        ValueError,
        "Unknown load mode {mode!r} for {self}!",
        test_input=("invalid_mode", "LazyMap[0]"),
    )
    source_type = _err.RaiserField[[_Stringable, str]](
        TypeError,
        "{self}: Bulk source must return a Mapping, got {actual_type}",
        test_input=("LazyMap[0]", "list"),
    )

    @_err.RaiserField.deco(
        TypeError,
        "Expected {data}, got {other} ({type})",
        test_input=(str, 22.5),
    )
    def deco1(expected: type, actual: Any, /):  # noqa:N805
        _args = Args.absorb(expected.__name__, actual, type(actual).__name__)
        return _err.RaiserParams.create(text_args=_args)


if __name__ == "__main__":
    from rich import print
    from rich.panel import Panel
    from rich.text import Text

    print("enum_member")
    print(f"{GateRaiser.enum_member}")
    print(f"{GateRaiser.enum_member.test_input}")
    print(f"{GateRaiser.enum_member.assemble_test()}")
    print()
    print("deco1")
    print(f"{GateRaiser.deco1}")
    print(f"{GateRaiser.deco1.test_input}")
    print(f"{GateRaiser.deco1.assemble_test()}")
    print()

    def _panel(text, style="cyan", /):
        print(Panel(text, style=style))

    def show(raiser_attr: Var):
        _panel(f"{raiser_attr.name}")
        print(f"--- {raiser_attr.value}")
        print(f"{raiser_attr.value!r}")
        print()
        print("Var")
        # for var in Kwargs.vars(raiser_attr.value):
        #     print(f"{var}")
        #     print()
        #     print(f"{var=}")
        #     print()
        #     print(var)

    def create_safe(error_attr):
        try:
            return error_attr.value.assemble_test()
        except Exception as error:
            _panel(f"CREATE FAIL: {error}", "b black on yellow")

    def launch_safe(sst_error):
        try:
            print("Start of:", sst_error)
            if isinstance(sst_error, BaseException):
                _panel("RAISE", "bold white on purple3")
                raise sst_error
            else:
                _panel(f"Nothing to raise: {sst_error}", "green")
                pass
        except Exception as error:
            if isinstance(error, _err.SstError):
                _panel(f"Error: {sst_error}", "red")
                pass
            else:
                _panel(f"LAUNCH FAIL: {error}", "b black on yellow")
                pass
            print(f"{error}")
            print(f"{error=}")
            print(error)
        finally:
            print(Text(" " * 80, style="on blue", justify="full"))

    # print("deco1-manual", _d1 := GateRaiser.deco1(int, "hello"))
    # launch_safe(_d1)

    for error_attr in GateRaiser:
        show(error_attr)
        # if sst_error := create_safe(error_attr):
        #     launch_safe(sst_error)
