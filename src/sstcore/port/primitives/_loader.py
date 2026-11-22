"""
Loader

-
"""

__all__: list[str] = [
    "LoaderClsInput",
    "LoaderInput",
    "Prefer",
    "LoadFunc",
    "Loading",
    "Loader",
]


import typing as _t
from collections.abc import Callable, Iterator
from typing import Any, Literal, Self, TypedDict
from typing import Unpack as _U  # noqa: N814

from ..empty import VOID, MayBe, MayNot
from ._typearg import TypeArg, TypeView, _LoaderAlias, type_view
from ._zero import LoaderView


class LoadFunc[**P, Target](_t.Protocol):
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Target:
        """Define the Typed and Parametrized Call of the Loader"""


type Loading[**P, T] = Loader[P, T] | LoadFunc[P, T]
type Prefer = Literal["func", "default"]


class LoaderInput[T](_t.TypedDict, total=False):
    """Define the Base for the Typed Kwargs"""

    default: MayBe[T]
    prefer: Prefer


class _LoaderClsInput[P, T](_t.TypedDict, total=False):
    loader: Loader[[P], T] | Loading[[P], T] | None


class LoaderClsInput(_LoaderClsInput, LoaderInput, TypedDict):
    """Extend the Base with the Loader Cls itself"""


class Loader[**P, T](LoaderView):
    """Govern the tools and state for predefined Loading"""

    Func = LoadFunc
    # CHECK: naming proper and mounting useful?
    Input = LoaderInput
    ClsInput = LoaderClsInput

    @property
    def value(self) -> T:
        """Provide the loaded Value or Raise"""
        if self._value is not VOID:
            return self._value
        _maybe = "but is" if self.is_ready else "and not"
        raise LookupError(f"Value not loaded, {_maybe} available: {self!r}")

    @property
    def is_ready(self) -> bool:
        """Is a Callable or static Default configured?"""
        return self._func is not None or self._default is not VOID

    def __init__(self, func: MayNot[Func[P, T]] = None, /, **tkw: _U[Input[T]]):
        """So far no check if Loader can complete, use Loader.__bool__"""
        self._func: MayNot[Loader.Func[P, T]] = func
        self._default: MayBe[T] = tkw.get("default", VOID)
        self._prefer: Prefer = tkw.get("prefer", "func")

        self._counter: int = 0
        self._total_counter: int = 0
        self._value: MayBe[T] = VOID

    def __bool__(self) -> bool:
        """Is the Value loaded by Call or any Fallback?"""
        return self._value is not VOID

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """Extract or Install Value by configured order or Raise if Empty"""
        self.load(*args, **kwargs)
        return self.value

    def load(self, *args: P.args, **kwargs: P.kwargs) -> MayBe[T]:
        """Fetch Value or Assign from launched Loaders in Prefered Order"""
        if self:
            return self._value
        for maybe_loaded_value in self._load(*args, **kwargs):
            if maybe_loaded_value is not VOID:
                self._value: T = maybe_loaded_value
                print(maybe_loaded_value)
                return maybe_loaded_value
        return VOID

    def _load(self, *args, **kwargs) -> Iterator:
        """Invoke Locations in Prefered Order to Install new Value"""
        match self._prefer:
            case "func":
                yield self._call(*args, **kwargs)
                yield self._default
                print("end func")
            case "default":
                yield self._default
                yield self._call(*args, **kwargs)
                print("end default")

    def _call(self, *args: P.args, **kwargs: P.kwargs) -> MayBe[T]:
        """Launch Loader Function and Increment Counter on Success"""
        if (result := self.call(*args, **kwargs)) is not VOID:
            self._counter += 1
            self._total_counter += 1
        return result

    def call(self, *args: P.args, **kwargs: P.kwargs) -> MayBe[T]:
        """Execute Loader Function if assigned without any State change"""
        if self._func is None:
            return VOID
        return self._func(*args, **kwargs)

    def reset(self) -> int:
        """Delete the current Value and  provide the reseted Counter"""
        _counted, self._counter = self._counter, 0
        self._value: VOID = VOID
        return _counted

    def bind(self, func: Callable[P, T], /) -> Callable[P, T]:
        """Attach or replace the Loader function and reset execution state"""
        self._func: Loader.Func[P, T] = func
        self.reset()
        return func

    def update(self, **tkw: _t.Unpack[Input[T]]) -> Self:
        """Assign new Parameter to this Unit and return it"""
        if (default := tkw.get("default", VOID)) is not VOID:
            self._default: T | VOID = default
        if (prefer := tkw.get("prefer", VOID)) is not VOID:
            self._prefer: Prefer = prefer
        return self

    def clone(self) -> Self:
        """Copy this Unit configuration with fresh state and empty value"""
        return type(self)(
            self._func, default=self._default, prefer=self._prefer
        )

    @classmethod
    def loading(
        cls, loading: MayNot[Loading[P, T]], /, **tkw: _U[Input[T]]
    ) -> Self:
        """Create Loader from Function, existing Loader or just by Kwargs"""
        return (
            loading.clone().update(**tkw)
            if isinstance(loading, cls)
            else cls(loading, **tkw)
        )

    #  LINE: -- Experimental -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __class_getitem__(cls, params: Any) -> Any:
        return _LoaderAlias(cls, params)

    @property
    def type_args(self) -> TypeArg:
        return TypeArg.from_loader(self)

    @property
    def _type_args(self) -> TypeView:
        return type_view(self, Loader)

    @property
    def target_type(self) -> Any:
        return self.type_args.value


if __name__ == "__main__":
    from rich.console import Console

    console = Console()

    def _print(loader):
        _prints: list[str] = [
            "\n--- Loader \n",
            f"{loader}",
            loader,
            "\n",
            f"{loader=}",
            # "\n --- TypeArg \n",
            # f"{loader.type_args}",
            # "\n",
            # f"{loader.type_args.render()}",
            # "\n",
            # f"{loader.type_args.value}",
            # "\n --- TypeView\n",
            # f"{loader._type_args}",
            # "\n",
            # f"{loader._type_args.render()}",
            # "\n",
            # f"{loader._type_args.value}",
        ]
        for line in _prints:
            console.print(line)

    def func1() -> int:
        return 5

    def func2() -> str:
        return "text"

    def func3(target: object, /, count: int = 3) -> str:
        return "::".join(f"{target}" for _ in range(count))

    loader = Loader(prefer="func")

    loader11 = Loader(func1, default=2, prefer="func")
    loader12 = Loader(func1, default=2, prefer="default")

    loader2 = Loader(func2)

    loader31 = Loader(func3)

    loader32: Loader[Callable[[Any, int], str], str] = Loader(func3)

    loaders: list[Loader] = [
        loader,
        loader11,
        loader12,
        loader2,
        loader31,
        loader32,
    ]

    for loader in loaders:
        _print(loader)

    for loader in loaders[:-2]:
        loader.load()
        print("loaded:", f"{loader}")

    loader31.load("prepared", count=2)
    loader32.load("loaded")

    for loader in loaders:
        _print(loader)
