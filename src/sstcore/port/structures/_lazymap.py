"""
Mappings

- MapGate: shared base with utils and rules
- LazyMap: delay loading until imports are safe and loader ready
- ActiveMap: grow at any time usually by inserted key and values

"""

from collections.abc import Callable, Hashable, Iterator, Mapping
from contextlib import contextmanager
from enum import Enum
from typing import Any, Protocol

from ..empty import VOID, MayBe, MayNot


class Loader[**P, V](Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> V: ...


class MapGate[K: Hashable, V]:
    def __init__(self, data: dict[K, V] | None = None):
        self._data: dict[K, V] = data or {}  # LATER: accept remaining kwargs?

    def __contains__(self, key: Any) -> bool:
        """Do not touch!"""
        with self.safe():
            if self.locksmith(key) in self._data:
                return True
        return False

    def __getitem__(self, key: Any) -> V:
        """Do not touch!"""
        lock: K = self.locksmith(key)
        if lock not in self:
            self._data[lock] = self.__missing__(lock)

        return self._data[lock]

    def __setitem__(self, key: Any, value: Any) -> None:
        """Do not touch!"""
        lock: K = self.locksmith(key)
        data: V = self.refine(value)
        if lock in self:
            if (_resolved := self.merge(lock, data)) is VOID:
                return
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

    def __missing__(self, lock: K) -> V:
        """Subhook on Missing"""
        raise NotImplementedError(lock)

    def merge(self, lock: K, data: V, /) -> MayBe[V]:
        """Subhook on Duplicated"""
        raise NotImplementedError(lock, data)

    def locksmith(self, key: Any) -> K:
        """Subhook on incoming Key"""
        raise NotImplementedError(key)

    def refine(self, value: Any) -> V:
        """Subhook on incoming Value"""
        raise NotImplementedError(value)

    def __iter__(self) -> Iterator[K]:  # Any?
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return f"{type(self).__name__}[{len(self)}]"

    def __repr__(self) -> str:
        text: str = "\n".join(f"{key}::{self[key]}" for key in self)
        return f"{self}[{f'\n{text}\n' if text else 'X'}]"

    def absorb(self, items: Mapping | None = None, /) -> Any:
        """Helper to register from Map"""
        for key, item in (items or {}).items():
            self[key] = item


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LazyMap[K: Hashable, V](MapGate[K, V]):
    """Loader may be for all keys or only for incoming"""

    def __init__(
        self,
        loader: Loader[[K], V] | None = None,
        default: MayBe[V] = VOID,
        fallback: MayNot[Callable[[K], V]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._loader: Loader[[K], V] | None = loader
        # AI: hard to say if all 3 are required or if some are even useful on MapGate
        self._default: MayBe[V] = default
        self._fallback: MayNot[Callable[[K], V]] = fallback

    @property
    def loader(self) -> Loader[[K], V]:
        if self._loader is None:
            raise RuntimeError(f"{self} failed without any loader...")
        return self._loader

    def __missing__(self, lock: K) -> V:
        if self._loader is not None:
            return self.loader(lock)
        if self._default is not VOID:
            return self._default
        if self._fallback is not None:
            return self._fallback(lock)
        raise KeyError("All loader and defaults failed...")


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ActiveMap[K: Hashable, V](MapGate[K, V]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def register(self, map: Mapping[K, V] | None = None, /, **named: V) -> None:
        self.absorb(map)
        self.absorb(named)


class EnumFieldMap(ActiveMap):
    """Store not shared Data for single Enum Member per Field or BoundField"""


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EnumMemberMap[E: Enum, V](ActiveMap[E, V]):
    """Store Enums by Member for Global Meta Registry"""

    def __init__(self, owner: type[E], label: str = "") -> None:
        super().__init__()
        self.owner: type[E] = owner
        self.label: str = label or owner.__name__

    def locksmith(self, key: Any) -> E:
        if type(key) is self.owner:
            return key
        if isinstance(key, str):  # TODO: SstEnumMeta.resolve
            try:
                return self.owner._member_map_[key]  # ty:ignore
            except KeyError:
                # TODO: better error texts, or move to safe
                raise KeyError(
                    f"{self.label}: unknown member {key!r}"
                ) from None
        raise TypeError(
            # TODO: better error texts, or move to safe
            f"{self.label}: expected {self.owner.__name__} or name, "
            f"got {type(key).__name__}"
        )
