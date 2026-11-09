# port.link analysis

## 1. Generalizing `PortLinkData`: `MorphMap` (`StoreMap` & `DraftMap`)

### What to Generalize vs. What to Fix

The `edit() <-> save()` pattern is a **two-phase immutable/mutable state machine** (similar to Clojure’s transients or Git’s staging area):

1. **`StoreMap` (Frozen state)**: Backed by `frozendict` (from `structures._map`), safe to cache, share across threads/classes, or expose publicly. Calling `.edit()` spawns a mutable draft.
2. **`DraftMap` (Mutable state)**: Backed by `dict`, used during collection/MRO traversal. Calling `.save()` seals it back into a `StoreMap`.

**Fixing the `__setitem__` problem:**
In `PortLinkCollect`, `__setitem__` silently ignored existing keys (`if access not in self.data: ...`). That is actually **`setdefault` / write-once** semantics disguised as `__setitem__`. In a general structure:

- `__setitem__` should validate via a `_validate(key, value)` subhook and **always write/overwrite** (or raise if strict).
- **`keep(key, value) -> bool`** (or `put_first`) should express the MRO "first-seen wins" behavior and return `True` if the item was inserted, `False` if skipped.
- **`fill(items, *, overwrite: bool = False) -> int`** uses `keep` (or `__setitem__`) and returns the exact **count of newly added entries**—answering your inline comment about measuring additions.

### Implementation for `structures/_map.py`

```python
# src/sstcore/port/structures/_map.py
from collections.abc import Callable, Iterable, Iterator, Mapping, MutableMapping
from contextlib import contextmanager
from typing import Any, Self, overload


class MorphMap[K, V](Mapping[K, V]):
    """Shared read-only interface for paired StoreMap and DraftMap structures."""

    __slots__ = ("_data",)
    _data: Mapping[K, V]

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return f"{type(self).__name__}[#{len(self)}]"

    def __repr__(self) -> str:
        return f"{self}({self._data!r})"

    @classmethod
    def _extract_key(cls, item: V) -> K:
        """Subhook: derive key from value when filling from a Sequence of values."""
        raise NotImplementedError(f"{cls.__name__} must implement _extract_key(item)")


class StoreMap[K, V, DraftT: DraftMap = DraftMap](MorphMap[K, V]):
    """Immutable mapping snapshot that can defrost into a mutable DraftMap."""

    __slots__ = ("_hash_cache",)
    _draft_cls: type[DraftT]

    def __init__(self, data: Mapping[K, V] | Iterable[tuple[K, V]] | Iterable[V] = ()) -> None:
        if isinstance(data, Mapping):
            self._data: frozendict[K, V] = frozendict(data)
        else:
            self._data = frozendict(self._ingest(data))
        self._hash_cache: int | None = None

    @classmethod
    def _ingest(cls, items: Iterable[tuple[K, V] | V]) -> Iterator[tuple[K, V]]:
        for item in items:
            match item:
                case (key, val):
                    yield key, val
                case val:
                    yield cls._extract_key(val), val

    def edit(self) -> DraftT:
        """Defrost into a mutable DraftMap pre-populated with current entries."""
        return self._draft_cls(self._data)

    def __hash__(self) -> int:
        if self._hash_cache is None:
            self._hash_cache = hash(self._data)
        return self._hash_cache


class DraftMap[K, V, StoreT: StoreMap = StoreMap](MorphMap[K, V], MutableMapping[K, V]):
    """Mutable staging mapping that validates inputs and freezes into a StoreMap."""

    __slots__ = ()
    _data: dict[K, V]
    _store_cls: type[StoreT]

    def __init__(self, data: Mapping[K, V] | Iterable[tuple[K, V]] | Iterable[V] = ()) -> None:
        self._data = {}
        if data:
            self.fill(data, overwrite=True)

    def _validate(self, key: K, value: V) -> None:
        """Subhook: raise an error if (key, value) is invalid for this map."""

    def __setitem__(self, key: K, value: V) -> None:
        """Standard write access (validates and overwrites)."""
        self._validate(key, value)
        self._data[key] = value

    def __delitem__(self, key: K) -> None:
        del self._data[key]

    def keep(self, key: K, value: V) -> bool:
        """Write-once access: insert only if key is absent. Returns True if added."""
        self._validate(key, value)
        if key not in self._data:
            self._data[key] = value
            return True
        return False

    def fill(
        self,
        data: Mapping[K, V] | Iterable[tuple[K, V]] | Iterable[V] | V,
        /,
        *,
        overwrite: bool = False,
    ) -> int:
        """Bulk-load entries. Returns the count of keys actually written."""
        write: Callable[[K, V], Any] = self.__setitem__ if overwrite else self.keep
        added = 0

        def _record(k: K, v: V) -> None:
            nonlocal added
            if write(k, v) is not False:
                added += 1

        match data:
            case Mapping():
                for k, v in data.items():
                    _record(k, v)
            case Iterable() if not isinstance(data, (str, bytes)):
                for item in data:
                    if isinstance(item, tuple) and len(item) == 2:
                        _record(item[0], item[1])
                    else:
                        _record(self._extract_key(item), item)
            case single_item:
                _record(self._extract_key(single_item), single_item)

        return added

    def save(self) -> StoreT:
        """Freeze current state into an immutable StoreMap."""
        return self._store_cls(self._data)


# Bind default pair
StoreMap._draft_cls = DraftMap
DraftMap._store_cls = StoreMap
```

### How `PortLinkData` looks with `MorphMap`

In `port/link/_define.py`, `PortLinkData` only defines its domain-specific multi-axis lookup (`[attr]`, `[source]`, `[(attr, source)]`) and validation:

```python
class PortLinkData(MorphMap[DocKey, Doc]):
    """Domain queries for (attr, source) -> Doc mappings."""
    __slots__ = ()

    @classmethod
    def _extract_key(cls, item: Doc) -> DocKey:
        return item.key

    def __iter__(self) -> Iterator[Doc]:
        return iter(self._data.values())

    def query(self, access: str | type | DocKey) -> list[Doc]:
        match access:
            case str() as attr:
                return [doc for doc in self if doc.attr == attr]
            case type() as source:
                return [doc for doc in self if doc.source is source]
            case (str() as attr, type() as source):
                return [doc] if (doc := self._data.get((attr, source))) else []
            case _:
                return []


class PortLinkStore(PortLinkData, StoreMap[DocKey, Doc, "PortLinkCollect"]):
    __slots__ = ()


class PortLinkCollect(PortLinkData, DraftMap[DocKey, Doc, PortLinkStore]):
    __slots__ = ()

    def _validate(self, key: DocKey, value: Doc) -> None:
        if not value.text:
            raise PortLinkError(f"Reject Empty Doc! {key=}, {value=}")


PortLinkStore._draft_cls = PortLinkCollect
PortLinkCollect._store_cls = PortLinkStore
```

---

## 2. Generalizing `LinkRegistry`: `WeakBiMap` with Domain Ergonomics

### The Problem

A generic `WeakBiMap[L, R]` uses neutral names (`lefts()`, `rights()`, `rights_of()`, `lefts_of()`). While mathematically clean, it hurts DX/UX: every time you use `LinkRegistry`, you have to pause and think _"Wait, is `port` left or right?"_.

At the same time, dynamically generating methods via `setattr` in `__init_subclass__` breaks static type checkers (`ty`, `pyright`, `mypy`), which won't know `registry.ports()` exists.

### The Solution: Subhook Labels + Direct Method Binding (Zero-Cost Aliases)

In Python's type system, assigning a base class method in a generic subclass body:

```python
class LinkRegistry(WeakBiMap[type, type], left="ports", right="plugs", edge="links"):
    register = WeakBiMap.link
    ports = WeakBiMap.lefts
    plugs = WeakBiMap.rights
    plugs_of = WeakBiMap.rights_of
    ports_of = WeakBiMap.lefts_of
    links = WeakBiMap.pairs
```

has **three major advantages**:

1. **100% Static Type Checker Support**: Type checkers resolve `LinkRegistry.ports` as `(self) -> tuple[type, ...]` with zero wrapper overhead.
2. **Zero Runtime Overhead**: They point to the exact same function objects in memory.
3. **Domain-Aware `stats()` and `__repr__()`**: By passing `left="ports", right="plugs", edge="links"` to `__init_subclass__`, `stats()` automatically outputs `{"ports": ..., "plugs": ..., "links": ...}`.

```python
# src/sstcore/port/structures/_map.py
from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import partial
from typing import ClassVar
from weakref import WeakKeyDictionary, WeakSet

_weak_map = partial(field, default_factory=WeakKeyDictionary, init=False, repr=False)


@dataclass(slots=True)
class WeakBiMap[L: type, R: type]:
    """
    GC-safe M:N bidirectional index between two weak-referenceable types.

    Subclass with domain labels and method aliases for ergonomic DX:
        class LinkRegistry(WeakBiMap[type, type], left="ports", right="plugs"):
            register = WeakBiMap.link
            ports = WeakBiMap.lefts
            plugs = WeakBiMap.rights
            plugs_of = WeakBiMap.rights_of
            ports_of = WeakBiMap.lefts_of
            links = WeakBiMap.pairs
    """

    _left_label: ClassVar[str] = "lefts"
    _right_label: ClassVar[str] = "rights"
    _edge_label: ClassVar[str] = "links"

    _forward: WeakKeyDictionary[L, WeakSet[R]] = _weak_map()
    _reverse: WeakKeyDictionary[R, WeakSet[L]] = _weak_map()

    def __init_subclass__(
        cls,
        *,
        left: str = "lefts",
        right: str = "rights",
        edge: str = "links",
        **kwargs,
    ) -> None:
        super().__init_subclass__(**kwargs)
        cls._left_label = left
        cls._right_label = right
        cls._edge_label = edge

    def link(self, left: L, right: R) -> None:
        """Record a bidirectional link between left and right."""
        self._forward.setdefault(left, WeakSet()).add(right)
        self._reverse.setdefault(right, WeakSet()).add(left)

    def unlink(self, left: L, right: R) -> bool:
        """Remove a link if present. Returns True if a link was removed."""
        removed = False
        if (rs := self._forward.get(left)) and right in rs:
            rs.remove(right)
            removed = True
        if (ls := self._reverse.get(right)) and left in ls:
            ls.remove(left)
            removed = True
        return removed

    def lefts(self) -> tuple[L, ...]:
        """All alive left-side items with at least one linked right-side item."""
        return tuple(k for k, vs in self._forward.items() if len(vs) > 0)

    def rights(self) -> tuple[R, ...]:
        """All alive right-side items with at least one linked left-side item."""
        return tuple(v for v, ks in self._reverse.items() if len(ks) > 0)

    def rights_of(self, left: L) -> tuple[R, ...]:
        """All alive right-side items linked to a specific left-side item."""
        vs = self._forward.get(left)
        return tuple(vs) if vs is not None else ()

    def lefts_of(self, right: R) -> tuple[L, ...]:
        """All alive left-side items linked to a specific right-side item."""
        ks = self._reverse.get(right)
        return tuple(ks) if ks is not None else ()

    def pairs(self) -> Iterator[tuple[L, R]]:
        """Yield all active (left, right) pairs."""
        for left, rights in list(self._forward.items()):
            for right in tuple(rights):
                yield (left, right)

    def __getitem__(self, item: L | R) -> tuple[L | R, ...]:
        """Return all linked counterparts regardless of which side `item` is on."""
        result: list[L | R] = []
        if (ls := self._reverse.get(item)) is not None:  # ty:ignore
            result.extend(ls)
        if (rs := self._forward.get(item)) is not None:  # ty:ignore
            result.extend(rs)
        return tuple(result)

    def __contains__(self, item: object) -> bool:
        match item:
            case (left, right):
                rs = self._forward.get(left)
                return bool(rs and right in rs)
            case single:
                return bool(
                    self._forward.get(single) or self._reverse.get(single)  # ty:ignore
                )

    def stats(self) -> dict[str, int]:
        return {
            self._left_label: len(self.lefts()),
            self._right_label: len(self.rights()),
            self._edge_label: sum(len(rs) for rs in self._forward.values()),
        }

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.stats()}]"
```

---

## 3. Generalizing `Channels`: `CliChannel` in `structures/_set.py`

### Why `Channels` is a High-Leverage Concept

Your `Channels` class in `_control.py` does four things at once in a tiny footprint:

1. **Polymorphic Target Resolution**: `target in channel` accepts a `str`, `type`, `Callable`, or instance, resolving `f"{module}.{qualname}".lower()` automatically.
2. **Scope vs. Flag Separation**: Splits hierarchical scopes (`"port"`, `"brick"`, `"*"`) from discrete operational flags (`"log"`, `"init"`, `"report"`).
3. **Guarded Scopes (`LINK_FLAGS`)**: Prevents noisy internal namespaces (like `"port.link"`) from triggering on `"*"` unless explicitly opted into (`SST_DEBUG="*,link"`).

### How to Upgrade & Generalize It into `CliChannel` (`NormSet` subclass)

To make `CliChannel` a general-purpose powerhouse for `sstcore.console`, `port`, and downstream projects, we should add three capabilities that eliminate manual post-processing (like the `LinkSpec.__post_init__` boilerplate):

1. **Exclusions (`!scope` or `-scope`)**: Allow `SST_DEBUG="*,!port.register"` to watch everything _except_ a noisy module.
2. **Inline `key=value` Parameters**: Allow `SST_DEBUG="port,log,report=2"` alongside bare flags `SST_DEBUG="port,log,report"`.
   - `channel.has_flag("report")` is `True` in both cases.
   - `channel.get_int("report", default=0, flag_default=2)` returns `0` if unset, `2` if bare `"report"` is passed, or `int(val)` if `"report=3"` is passed!
3. **Multi-Env & Algebraic Stacking (`ch1 | ch2`)**:
   - Support passing one or multiple `env_var` names (`env_var=("SST_DEBUG", "SST_PORT")`).
   - Support combining channels via `parent_channel | child_channel` so `sstcore.console` can define a root channel and `port.link` can layer its specific guards/defaults on top.

### Implementation for `structures/_set.py`

```python
# src/sstcore/port/structures/_set.py
import os
from collections.abc import Callable, Iterable
from typing import Any, ClassVar, Self

from .._types import _Stringable, _Stringables
from ._map import frozendict


class CliChannel(NormSet):
    """
    Env-driven scope router, flag switchboard, and micro-parameter parser.

    Syntax supported in env vars or default iterables (comma-separated):
      - Scopes:      "port, brick.vault, *" (matched via substring or wildcard)
      - Exclusions:  "!port.link, -brick.old" (prefixed with '!' or '-', overrides '*')
      - Flags:       "log, init, report" (matched against known `flag_names`)
      - Key=Value:   "report=2, theme=dark" (stored in `.params` AND `.flags`)
      - Guards:      Namespaces in `guard_names` ignore '*' unless explicitly named.
    """

    DEFAULT_FLAGS: ClassVar[frozenset[str]] = frozenset()
    DEFAULT_GUARDS: ClassVar[frozenset[str]] = frozenset()

    flags: frozenset[str]
    params: frozendict[str, str]
    excludes: frozenset[str]
    guards: frozenset[str]
    _locked_guards: frozenset[str]

    def __new__(
        cls,
        default: _Stringables = (),
        /,
        *,
        env_var: str | Iterable[str] = (),
        flags: Iterable[str] = (),
        guards: Iterable[str] = (),
    ) -> Self:
        raw_tokens = cls._collect_raw(default, env_var)
        known_flags = cls.DEFAULT_FLAGS | {cls.normalize(f) for f in flags}
        known_guards = cls.DEFAULT_GUARDS | {cls.normalize(g) for g in guards}

        scopes: set[str] = set()
        active_flags: set[str] = set()
        excludes: set[str] = set()
        params: dict[str, str] = {}

        for token in raw_tokens:
            clean = cls.normalize(token)
            if not clean:
                continue

            if "=" in clean:
                k, _, v = clean.partition("=")
                k, v = k.strip(), v.strip()
                if k:
                    active_flags.add(k)
                    params[k] = v
            elif clean.startswith(("!", "-")):
                if ex := clean[1:].strip():
                    excludes.add(ex)
            elif clean in known_flags:
                active_flags.add(clean)
            else:
                scopes.add(clean)

        unit: Self = super().__new__(cls, scopes)
        unit.flags = frozenset(active_flags)
        unit.params = frozendict(params)
        unit.excludes = frozenset(excludes)
        unit.guards = known_guards
        # A guard remains locked unless an active scope explicitly overlaps with it
        unit._locked_guards = frozenset(
            g for g in known_guards if not any(g in s or s in g for s in scopes)
        )
        return unit

    @staticmethod
    def _collect_raw(
        default: _Stringables, env_var: str | Iterable[str]
    ) -> list[str]:
        env_names = (env_var,) if isinstance(env_var, str) else tuple(env_var)
        env_Parts = [
            part
            for name in env_names
            if name
            for part in os.getenv(name, "").split(",")
        ]
        def_parts = [
            part
            for item in default
            for part in f"{item}".split(",")
        ]
        return [*env_Parts, *def_parts]

    @classmethod
    def normalize(cls, item: _Stringable, /) -> str:
        return f"{item}".strip().lower()

    @classmethod
    def key(cls, target: Any, /) -> str:
        """Resolve class, callable, or instance to lowercased 'module.qualname'."""
        if isinstance(target, str):
            return cls.normalize(target)
        if not isinstance(target, (type, Callable)):
            target = type(target)
        module: str = getattr(target, "__module__", "")
        qualname: str = getattr(
            target, "__qualname__", getattr(target, "__name__", "")
        )
        return f"{module}.{qualname}".lower()

    def __contains__(self, target: Any) -> bool:
        """Does target (str, class, callable, or instance) match an active scope?"""
        if not self or target is None:
            return False

        key: str = self.key(target)

        # 1. Explicit exclusions always win
        if any(ex in key for ex in self.excludes):
            return False

        # 2. Locked guards reject matching targets (even when '*' is active)
        if any(g in key for g in self._locked_guards):
            return False

        # 3. Wildcard or substring scope match
        if super().__contains__("*"):
            return True
        return any(scope in key for scope in super().__iter__())

    def has_flag(self, flag: str, /) -> bool:
        """Check if a boolean flag, key=value param, or exact scope is active."""
        fmt = self.normalize(flag)
        return fmt in self.flags or super().__contains__(fmt)

    def get_int(
        self, key: str, /, default: int = 0, *, flag_default: int = 1
    ) -> int:
        """
        Resolve integer option from channel:
          - 'report=3' -> 3
          - 'report'   -> flag_default (e.g. 2)
          - unset      -> default (e.g. 0)
        """
        fmt = self.normalize(key)
        if fmt in self.params:
            try:
                return int(self.params[fmt])
            except ValueError:
                return flag_default
        return flag_default if self.has_flag(fmt) else default

    def __or__(self, other: Any) -> Self:
        """Stack/merge two CliChannels (right-hand side overrides params/un-excludes)."""
        if not isinstance(other, CliChannel):
            return NotImplemented
        combined_scopes = (set(self) - other.excludes) | set(other)
        combined_excludes = (self.excludes - set(other)) | other.excludes
        combined_flags = self.flags | other.flags
        combined_params = self.params | other.params
        combined_guards = self.guards | other.guards

        tokens = [
            *combined_scopes,
            *(f"!{ex}" for ex in combined_excludes),
            *(f for f in combined_flags if f not in combined_params),
            *(f"{k}={v}" for k, v in combined_params.items()),
        ]
        return type(self)(
            tokens,
            flags=combined_flags,
            guards=combined_guards,
        )

    def __repr__(self) -> str:
        parts = [f"scopes={set(self)!r}"]
        if self.flags:
            parts.append(f"flags={set(self.flags)!r}")
        if self.params:
            parts.append(f"params={dict(self.params)!r}")
        if self.excludes:
            parts.append(f"excludes={set(self.excludes)!r}")
        return f"{type(self).__name__}({', '.join(parts)})"
```

### How this simplifies `port/link/_control.py` (and fixes `Tap.printer`)

1. **`Channels` in `_control.py`** becomes a 3-line preset of `CliChannel`:

```python
class Channels(CliChannel):
    DEFAULT_FLAGS = frozenset({"log", "report", "init"})
    DEFAULT_GUARDS = frozenset({"link", "port.link"})
```

1. **`LinkSpec.__post_init__`** can now resolve `report` via `ch.get_int("report", default=0, flag_default=2)` so `SST_DEBUG="report=1"` and `SST_DEBUG="report"` both work seamlessly.
2. **Fixing `Tap.printer`**: In your `# FIX:` comment in `Tap.replace`, you noted that `printer` only activates globally when `spec.report > 0`. With `CliChannel`, `Tap` can gate printing per-channel or allow `tap.printer` whenever `bool(spec.channels)` or `spec.report > 0`, while `show_result` remains guarded by `"port.link" in spec.channels or spec.report > 0`.

---

## 4. `CliChannel` vs. `pydantic.BaseSettings`

| Dimension                       | `CliChannel` (`structures._set`)                                                                                                      | `pydantic.BaseSettings`                                                                                               |
| :------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------- |
| **Dependency & Import Cost**    | **0 ms**, stdlib-only, safe at `DependencyLevel[0.1]`.                                                                                | **~50–120 ms** import time; pulls in `pydantic` + `pydantic-settings` (unusable in low-level `port`).                 |
| **Shell UX (1 vs. N Env Vars)** | **Single micro-DSL**: `SST_DEBUG="*,!port.link,init,report=2"` configures scopes, exclusions, flags, and levels in one variable.      | **Env var sprawl**: Needs `SST_SCOPES='["*"]' SST_TRACE_INIT=1 SST_REPORT=2` or verbose JSON in the terminal.         |
| **Active Routing (`in`)**       | **Polymorphic matcher**: `if self in channel:` or `if func in channel:` inspects `__module__` and `__qualname__` directly.            | **Passive data**: Only parses fields; you still have to write all scope-matching, wildcard, and guard logic yourself. |
| **Stacking / Layering**         | **Algebraic (`root_ch \| local_ch`)**: Easy to compose global `SST_DEBUG` with module-specific `SST_PORT` or runtime `toggle` tuples. | Requires subclass inheritance or manual model merging.                                                                |

### When to use which?

- Use **`CliChannel`** for **instrumentation, console switches, logging scopes, and developer toggles** (`SST_DEBUG`, `SST_CONSOLE`), and combine it with your **`DataClassSpec`** when you want to bind those parsed flags onto a typed configuration object like `LinkSpec`.
- Reserve **`pydantic.BaseSettings`** for high-level application deployment configs (database URLs, API credentials,`.env` file secrets) at the outer boundary of an application.
