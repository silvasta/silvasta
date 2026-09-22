"""
WRITE FINAL STACK HERE

- Temporary until ready to move to proper place

"""

# NEXT: implement

__all__: list[str] = [
    # "StackData",
    # "StackCore",
]

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Concatenate, Self, cast

from . import ___data as data
from . import ___define as port

#  LINE: -- Single -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True, slots=True)
class Layer2:
    """Definition of one stacking layer."""

    mapping: Mapping[str, Any]
    mode: port.LayerMode = port.LayerMode.REPLACE
    name: str = ""
    # CHECK: what is useful with CUSTOM??
    merge: Callable[[Any, Any], Any] | None = None  # Only used with CUSTOM


@dataclass
class AttrGroup[T]:  # Stack4
    """One dimension of configuration (e.g. colors, modifiers, pipeline steps)."""

    mapping: dict[str, T]
    default: T | None = None
    strategy: str = "set"  # "set" | "append" | "extend"
    # Optional dynamic resolver (e.g. lookup in ColorBox)
    resolver: Callable[[str, dict[str, T]], Any] | None = None


if TYPE_CHECKING:
    _unit: port.StackingMap = Layer2(data.ANSI_COLORS)
    _cls: type[port.StackingMap] = Layer2


#  LINE: -- Combination -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class StackCore1[ResulT]:
    _registry: port.AttrRegistry
    _executor: Callable[
        [port.StateDict, tuple[Any, ...], dict[str, Any]], ResulT
    ]
    _state: port.StateDict = field(default_factory=dict)

    def __getattr__(self, name: str) -> Self:
        if name not in self._registry:
            raise AttributeError(
                f"'{type(self).__name__}' has no attribute '{name}'"
            )

        group_name, value = self._registry[name]

        new_state = {**self._state, group_name: value}

        return type(self)(
            _registry=self._registry,
            _executor=self._executor,
            _state=new_state,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> ResulT:
        """Pass the accumulated state and all runtime arguments to the executor."""
        return self._executor(self._state, args, kwargs)

    @classmethod
    def build(
        cls,
        mappings: Mapping[str, Mapping[str, Any]],
        executor: Callable[
            [port.StateDict, tuple[Any, ...], dict[str, Any]], ResulT
        ],
    ) -> Self:
        registry: dict[str, tuple[str, Any]] = {}
        for group, attrs in mappings.items():
            for attr_name, attr_value in attrs.items():
                if attr_name in registry:
                    raise ValueError(
                        f"Duplicate attribute name detected: {attr_name}"
                    )
                registry[attr_name] = (group, attr_value)

        return cls(_registry=registry, _executor=executor)


if TYPE_CHECKING:
    _unit: port.StackingCore = StackCore1()
    _cls: type[port.StackingCore] = StackCore1


class StackCore2[InputT, ResultT]:
    # TASK: ever needed? __slots__ = ("_layers", "_state", "_finalizer")

    def __init__(
        self,
        layers: Sequence[Layer2 | Mapping[str, Any]],
        finalizer: Callable[[list[Any], InputT], ResultT],
        state: list[Any] | None = None,
    ) -> None:
        self._layers: list[Layer2] = [
            layer
            if isinstance(layer, Layer2)  #
            else Layer2(mapping=layer)
            for layer in layers
        ]
        self._finalizer = finalizer
        self._state: list[Any] = (
            state if state is not None else [None] * len(self._layers)
        )

    def __getattr__(self, name: str) -> Self:
        for i, layer in enumerate(self._layers):
            if name not in layer.mapping:
                continue

            value = layer.mapping[name]
            new_state = self._state.copy()

            match layer.mode:
                case port.LayerMode.REPLACE:
                    new_state[i] = value
                case port.LayerMode.ACCUMULATE:
                    current = new_state[i]
                    if current is None:
                        new_state[i] = (value,)
                    else:
                        new_state[i] = current + (value,)
                case port.LayerMode.CUSTOM:
                    if layer.merge is None:
                        # FIX: check in advance
                        raise RuntimeError(
                            f"Layer {i} has CUSTOM mode but no merge function"
                        )
                    new_state[i] = layer.merge(new_state[i], value)

            return type(self)(
                layers=self._layers,
                finalizer=self._finalizer,
                state=new_state,
            )

        raise AttributeError(
            f"'{type(self).__name__}' has no attribute '{name}'"
        )

    def __call__(self, arg: InputT) -> ResultT:
        return self._finalizer(self._state, arg)

    # --- Introspection / Utilities ---

    def clone(self) -> Self:
        return type(self)(
            layers=self._layers,
            finalizer=self._finalizer,
            state=self._state.copy(),
        )

    def reset(self) -> Self:
        return type(self)(
            layers=self._layers,
            finalizer=self._finalizer,
            state=None,
        )

    @property
    def state(self) -> tuple[Any, ...]:
        return tuple(self._state)


if TYPE_CHECKING:
    _unit: port.StackingCore = StackCore2()
    _cls: type[port.StackingCore] = StackCore2


class StackCore3[TContext, **P, TReturn]:
    """Strictly separates State Accumulation from Execution."""

    def __init__(
        self,
        context: TContext,
        registry: dict[str, port.Mutator[TContext]],
        executor: Callable[Concatenate[TContext, P], TReturn],
    ) -> None:
        self._context: TContext = context
        self._registry: dict[str, port.Mutator[TContext]] = registry
        self._executor: Callable[Concatenate[TContext, P], TReturn] = executor

    def __getattr__(self, name: str) -> Self:
        """Dynamic chaining: applies the mutator and returns a new stack."""
        if mutator := self._registry.get(name):
            # Create a new instance with the mutated context (Immutability)
            return type(self)(
                context=mutator(self._context),
                registry=self._registry,
                executor=self._executor,
            )
        raise AttributeError(
            f"'{type(self).__name__}' has no attribute '{name}'"
        )

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> TReturn:
        """Executes the injected logic with the accumulated context."""
        return self._executor(self._context, *args, **kwargs)


if TYPE_CHECKING:
    _unit: port.StackingCore = StackCore3()
    _cls: type[port.StackingCore] = StackCore3


class StackCore4[InputT, OutputT]:
    """Generalized fluent stacking core.

    Created via the `.create()` factory (recommended) or subclassed.
    Supports different update strategies per group and context injection.
    """

    _groups: dict[str, AttrGroup] = {}
    _applicator: port.Applicator[InputT, OutputT] | None = None
    _defaults: dict[str, Any] = {}

    def __init__(
        self,
        state: dict[str, Any] | None = None,
        context: Any | None = None,
    ) -> None:
        self._state = state or self._defaults.copy()
        self._context = context

    def __getattr__(self, name: str) -> Self:
        for key, group in self._groups.items():
            value = None
            if name in group.mapping:
                value = group.mapping[name]
            elif group.resolver:
                value = group.resolver(name, self._state)
                if value is None:
                    continue

            if value is not None:
                new_state = self._state.copy()
                if group.strategy == "set":
                    new_state[key] = value
                elif group.strategy in ("append", "extend"):
                    current = list(new_state.get(key, []))
                    if group.strategy == "append" or not isinstance(
                        value, (list, tuple)
                    ):
                        current.append(value)
                    else:
                        current.extend(value)
                    new_state[key] = tuple(current)  # immutable
                else:
                    new_state[key] = value

                return type(self)(new_state, self._context)

        raise AttributeError(
            f"'{type(self).__name__}' has no attribute '{name}'"
        )

    def __call__(self, value: InputT) -> OutputT:
        if self._applicator is None:
            raise NotImplementedError("No applicator configured")
        return self._applicator(self._state, value, self._context)

    def with_context(self, **kwargs: Any) -> Self:
        """Inject context (ColorBox, Printer instance, etc.)."""
        new_ctx = (
            self._context.copy() if isinstance(self._context, dict) else {}
        )
        new_ctx.update(kwargs)
        return type(self)(self._state, new_ctx)

    def with_base(self, **base_state: Any) -> Self:
        """Add default state (useful for per-method stacks)."""
        new_state = self._state.copy()
        new_state.update(base_state)
        return type(self)(new_state, self._context)

    @classmethod
    def create(
        cls,
        name: str,
        groups: dict[str, AttrGroup],
        applicator: port.Applicator[InputT, OutputT],
        defaults: dict[str, Any] | None = None,
        module: str | None = None,
    ) -> type[Self]:
        """Factory to create a concrete, reusable stack class."""
        return cast(
            type[Self],
            type(
                name,
                (cls,),
                {
                    "_groups": groups,
                    "_applicator": staticmethod(applicator),
                    "_defaults": defaults or {},
                    "__module__": module or cls.__module__,
                },
            ),
        )


if TYPE_CHECKING:
    _unit: port.StackingCore = StackCore4()
    _cls: type[port.StackingCore] = StackCore4
