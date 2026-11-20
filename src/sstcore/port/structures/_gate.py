"""
Mappings

- MapGate: shared base with utils and rules
- LazyMap: delay loading until imports are safe and loader ready
- ActiveMap: grow at any time usually by inserted key and values

"""

from collections.abc import Callable, Hashable, Iterator, KeysView, Mapping
from contextlib import contextmanager
from typing import Any, ClassVar, Unpack

from .._error import RaiserField, RaiserMeta, SstError, SstPortError
from ..empty import VOID, MayBe, MayNot
from ..primitives import Loader, LoaderInput, Loading


class MapGate[K: Hashable, V]:
    def __init__(self, data: dict[K, V] | None = None):
        self._data: dict[K, V] = data or {}

    def __contains__(self, key: Any) -> bool:
        """Is the processed Key in Data?"""
        with self.safe():
            if self.locksmith(key) in self._data:
                return True  # needed for type checker
        return False

    def __getitem__(self, key: Any) -> V:
        """Read Value or Forward to SetItem or Missing"""
        if key not in self:
            self[key] = self.__missing__(key)
        return self._data[self.locksmith(key)]

    def __missing__(self, key: Any) -> V:
        """Subhook on Missing - provide writable value or Raise"""
        raise KeyError(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """Sanitize Inputs, write Value or handle merge result on duplication"""
        lock: K = self.locksmith(key)
        data: V = self.refine(value)
        if key in self:
            resolved: MayBe[V] = self.merge(lock, data)
            if resolved is not VOID:
                data: V = resolved
        self._data[lock] = data

    def __delitem__(self, key: Any) -> None:
        """Just for completenes"""
        del self._data[self.locksmith(key)]

    @contextmanager
    def safe(self):
        """Subhook on Error"""
        try:
            yield
        except KeyError, TypeError:
            pass

    def merge(self, _lock: K, data: V, /) -> MayBe[V]:
        """Subhook on Duplicated: default=overwrite"""
        return data

    def locksmith(self, key: Any) -> K:
        """Subhook on incoming Key:"""
        return key

    def refine(self, value: Any) -> V:
        """Subhook on incoming Value"""
        return value

    def keys(self) -> KeysView:
        """Provide Keys for **unpacking"""
        return self._data.keys()

    def values(self) -> Iterator[V]:
        yield from self._data.values()

    def __iter__(self) -> Iterator[K]:  # Any?
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return f"{type(self).__name__}[{len(self)}]"

    def __repr__(self) -> str:
        text: str = "\n".join(f"{key}::{self[key]}" for key in self)
        return f"{self}[{f'\n{text}\n' if text else 'X'}]"

    def absorb(self, map: Mapping | None = None, /) -> Any:
        """Register from Map if values provided"""
        for key, item in (map or {}).items():
            self[key] = item


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LazyMap[K: Hashable, V](MapGate[K, V]):
    """Loader may be for all keys or only for incoming"""

    def __init__(
        self,
        loader: Loader[[K], V] | Loading[[K], V] | None = None,
        fallback: MayNot[Callable[[K], V]] = None,
        **tkw: Unpack[LoaderInput[V]],
    ):
        super().__init__()
        self.loader: Loader[[K], V] = (
            loader.updated(**tkw)
            if isinstance(loader, Loader)
            else Loader(loader, **tkw)
        )
        self._fallback: MayNot[Callable[[K], V]] = fallback

    def __missing__(self, key: Any) -> V:
        if (value := self.loader.install(key)) is not VOID:
            return value
        if self._fallback is not None:
            return self._fallback(key)
        raise KeyError("All loader and defaults failed...")


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ActiveMap[K: Hashable, V](MapGate[K, V]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def register(self, map: Mapping[K, V] | None = None, /, **named: V) -> None:
        self.absorb(map)
        self.absorb(named)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CacheGate[K: Hashable, V](MapGate[K, V]):
    """Observable Flyweight Cache Gate with hit/miss tracking and size guard."""

    _all_caches: ClassVar[list[CacheGate[Any, Any]]] = []

    def __init__(
        self,
        owner: type[V],
        # TODO: forward to super()__init__: loader: Callable[[K], V],
        max_size: int | None = None,
    ) -> None:
        super().__init__()
        self.owner: type[V] = owner
        # self._loader: Callable[[K], V] = loader
        self.max_size: int | None = max_size
        self.hits: int = 0
        self.misses: int = 0
        self._all_caches.append(self)

    def fetch(self, key: K, factory: Callable[[], V]) -> V:
        if key in self._data:
            self.hits += 1
            return self._data[key]
        self.misses += 1
        if self.max_size is not None and len(self._data) >= self.max_size:
            # Evict oldest inserted key (FIFO) or trigger warning hook
            self._data.pop(next(iter(self._data)))
        value: V = factory()
        self._data[key] = value
        return value

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total else 0.0

    def __str__(self) -> str:
        return (
            f"CacheGate[{self.owner.__name__}: "
            f"size={len(self)}, hits={self.hits}, misses={self.misses}, "
            f"hit_rate={self.hit_rate:.1%}]"
        )


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class GateRaiser(metaclass=RaiserMeta):
    """Explain Failures Meaningful"""

    _base_error: type[SstError] = SstPortError

    enum_member = RaiserField[[str, str]](
        KeyError,
        "{label}: Unknown Enum Member: {member!r}",
    )
    enum_type = RaiserField[[str, str, str]](
        TypeError,
        "{label}: Expected {owner} but received {incoming}",
    )
    cache1 = RaiserField[[str]](
        KeyError,
        "Cache miss for lookup key {0!r}",
    )

    out_of_range = RaiserField[[str, int]](
        ValueError,
        "Field {0} exceeded max limit {1}",
    )
    not_initialized = RaiserField[[]](
        RuntimeError,
        "System is not initialized",
    )

    # NEXT: figure out best method

    @RaiserField(TypeError, "Expected {0}, got {1} ({2}")
    def deco1(expected: type, actual: Any, /):  # noqa:N805
        # IDEA: 1 - as preprocess
        return expected.__name__, actual, type(actual).__name__

    @RaiserField(TypeError, "")
    def deco2(expected: type, actual: Any, /):  # noqa:N805
        # IDEA: 2 - as custom format
        return f"Expected {expected.__name__}, got {actual!r} ({type(actual).__name__})"


if __name__ == "__main__":
    from rich import print
    from rich.panel import Panel

    print(GateRaiser.cache1("works"))
    print(GateRaiser.out_of_range("hello", 1))
    print(GateRaiser.not_initialized())

    def _panel(text, style="cyan", /):
        print(Panel(text, style=style))

    for attr in GateRaiser:
        try:
            _panel(f"{attr}")
            print(task := attr("hello"))

            if isinstance(task, BaseException):
                _panel("RAISE", "bold white on purple3")
                raise task
            else:
                _panel(f"Nothing to raise: {task}", "green")
        except Exception as error:
            _panel(f"Error: {task}", "red")
            print(f"{error}")
            print(f"{error=}")
            print(error)
        finally:
            print("--- " * 5)

    print(f"{GateRaiser.cache1("loader is missing")=}")
