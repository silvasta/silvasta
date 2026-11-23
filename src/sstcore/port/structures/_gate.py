"""
Govern the Behaviour of tiny helper Mappings

- MapGate: shared base with utils and rules
- LazyMap: delay loading until imports are safe and loader ready
- ActiveMap: grow at any time usually by inserted key and values
- CacheGate: flyweight fetch with hit accounting and a FIFO cap

"""

from collections.abc import Callable, Iterator, KeysView, Mapping
from contextlib import contextmanager
from enum import Enum, auto
from inspect import Parameter, signature
from typing import Any, ClassVar, Literal
from typing import Unpack as _U  # noqa: N814

from .._error import (
    RaiserField,
    RaiserMeta,
    RaiserParams,
    SstError,
    SstPortError,
)
from .._types import _Stringable
from ..empty import VOID, MayBe, MayNot
from ..primitives import Args, Kwargs, Loader, Loading, Var
from ..primitives._loader import LoaderClsInput

type LoadMode = Literal["auto", "item", "table"]
type Fallback[K, V] = Callable[[K], V] | Loader[[K], V]


def _is_nullary(func: Callable[..., Any] | None) -> bool:
    """True when func can be called with no arguments."""
    if func is None:
        return False
    try:
        params = signature(func).parameters.values()
    except TypeError, ValueError:
        return False
    return not any(
        param.kind
        in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
        and param.default is Parameter.empty
        for param in params
    )


class MapGate[K: str, V]:
    def __init__(self, data: dict[K, V] | None = None):
        self._data: dict[str, V] = {}
        if data:
            self.absorb(data)

    def absorb(self, map: Mapping | None = None, /, **kwargs) -> Any:
        """Send mapped Items trough register pipeline"""
        for key, item in (map or {} | kwargs).items():
            self[key] = item

    def __delitem__(self, key: Any) -> None:
        del self._data[self.locksmith(key)]

    def __contains__(self, key: Any) -> bool:
        # INFO: ignore multiple locksmith hits for now
        # - far away, that will not be relevant soon
        """Is the processed Key in Data?"""
        with self.safe():
            if self.locksmith(key) in self._data:
                return True  # type check mock
        return False

    def __getitem__(self, key: Any, /) -> V:
        """
        Read Value or call Missing and Raise on Fail

        - Later: use the Loader/TypeArg setup to ensure V is valid

        """
        if key in self:
            return self._data[self.locksmith(key)]

        recovery: MayBe[V] = self.__missing__(key)

        if recovery is VOID:
            raise GateRaiser.key_miss(key, self)

        return recovery

    def __setitem__(self, key: Any, value: Any) -> None:
        """Sanitize Inputs, write Value or handle merge result on duplication"""

        lock: K = self.locksmith(key)
        data: V = self.refine(value)

        if key not in self:
            self._data[lock] = data
            return

        resolved: MayBe[V] = self.merge(lock, data)

        if resolved is not VOID:
            self._data[lock] = resolved

    def __missing__(self, _key: Any, /) -> MayBe[V]:
        """
        Find a Solution for an absent Key

        - Provide some proper Value or return VOID to Raise

        """
        return VOID

    def merge(self, _lock: K, data: V, /) -> MayBe[V]:
        """
        Find a Solution for a duplicated Key

        - Provide the Value to store or VOID for Ignore
        """
        return data

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

    def keys(self) -> KeysView:
        """Provide Keys for **unpacking"""
        return self._data.keys()

    def values(self) -> Iterator[V]:
        """Stream all Values"""
        yield from self._data.values()

    def __iter__(self) -> Iterator[Var]:  # Any?
        """Provide all Named key and value Tuple"""
        for name, value in self._data.items():
            var = Var(name, value)
            var.sep = "::"
            yield var

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        return f"{type(self).__name__}[{len(self)}]"

    # CHECK: compare new formatting with this
    # def __repr__(self) -> str:  # LATER: use Var and Kwargs
    #     text: str = "\n".join(f"{key}::{self[key]}" for key in self)
    #     return f"{self}[{f'\n{text}\n' if text else 'X'}]"

    def __repr__(self) -> str:
        # IDEA: assing Kwargs in __init__, like the live viewer
        kwargs = Kwargs(self._data)
        kwargs.sep = "\n"

        # REMOVE:
        _text: str = "\n".join(f"{var}" for var in self)
        _text: str = f"{kwargs}"

        return f"{self}[{f'\n{kwargs}\n' if kwargs else 'X'}]"


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class LazyMap[K: str, V](MapGate[K, V]):
    """Loader may be for all keys or only for incoming"""

    def __init__(
        self,
        loader: Loader[[K], V] | Loading[[K], V] | None = None,
        fallback: MayNot[Fallback[K, V]] = None,
        *,
        mode: LoadMode = "auto",
        **tkw: Any,
    ) -> None:
        super().__init__()
        if mode not in ("auto", "item", "table"):
            raise ValueError(f"unknown load mode: {mode!r}")
        self.loader: Loader[[K], V] = Loader.loading(loader, **tkw)
        self._fallback: MayNot[Fallback[K, V]] = fallback
        self._mode: LoadMode = mode

    def __missing__(self, key: Any) -> MayBe[V]:
        """Launch the Loader to fetch the Value or use Fallback"""

        value: V | VOID = self.loader.load(key)

        if value is not VOID:
            return value

        if self._fallback is not None:
            return self._fallback(key)

        return VOID


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ActiveMap[K: str, V](MapGate[K, V]):
    def __init__(
        self,
        data: Mapping[K, V] | None = None,
        /,
        **named: V,
    ) -> None:
        super().__init__()
        if data is not None or named:
            self.register(data, **named)

    def register(self, map: Mapping[K, V] | None = None, /, **named: V) -> None:
        self.absorb(map)
        self.absorb(named)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class CacheGate[K: str, V](MapGate[K, V]):
    """Observable Flyweight Cache Gate with hit/miss tracking and size guard."""

    _all_caches: ClassVar[list[CacheGate[Any, Any]]] = []

    def __init__(
        self,
        owner: type[V],
        max_size: int | None = None,
        **tkw: _U[LoaderClsInput],
    ):
        # AI: the common loader root is missing... maybe 1 class that only operates as root fork
        # super().__init__(
        #     **tkw  # NOTE: maybe the loader needs to be split and inserted positionally
        # )
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
        total: int = self.hits + self.misses
        return self.hits / total if total else 0.0

    def __str__(self) -> str:
        owner: str = getattr(self.owner, "__name__", "?")
        return (
            f"CacheGate[{owner}: size={len(self)}, hits={self.hits}, "
            f"misses={self.misses}, hit_rate={self.hit_rate:.1%}]"
        )

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def report(cls) -> str:
        return (
            "\n".join(str(cache) for cache in cls._all_caches)
            or "CacheGate[none]"
        )


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _TestEnum(Enum):
    FAILING = auto()


class GateRaiser(metaclass=RaiserMeta):
    """Explain Failures Meaningful"""

    _error = SstPortError

    enum_member = RaiserField[[str, str]](
        KeyError,
        "{label}: Unknown Enum Member: {member!r}",
        test_input=("LABEL", _TestEnum.FAILING),
    )
    enum_type = RaiserField[[str, str, str]](
        TypeError,
        "{label}: Expected {owner} but received {incoming}",
        test_input=(Loader(), _TestEnum, Enum),
    )
    key_miss = RaiserField[[_Stringable, _Stringable]](
        KeyError,
        "Invalid {key!r} for {self}!",
        test_input=(423, Loader(default="data")),
    )

    @RaiserField.deco(
        TypeError,
        "Expected {data}, got {other} ({type})",
        test_input=(str, 22.5),
    )
    def deco1(expected: type, actual: Any, /):  # noqa:N805
        args = Args.absorb(expected.__name__, actual, type(actual).__name__)
        return RaiserParams.create(text_args=args)


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
            if isinstance(error, SstError):
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
