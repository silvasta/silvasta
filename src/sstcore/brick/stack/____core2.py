from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Self

from .___data import ANSI_COLORS, ANSI_MODIFIERS


class LayerMode(Enum):
    """How selections from this layer should be merged."""

    # EXTRACT:
    REPLACE = auto()  # Last selection wins
    ACCUMULATE = auto()  # Collect into a tuple (order of selection preserved)
    CUSTOM = auto()  # Use provided merge function


@dataclass(frozen=True, slots=True)
class Layer:
    """Definition of one stacking layer."""

    # EXTRACT:
    mapping: Mapping[str, Any]
    mode: LayerMode = LayerMode.REPLACE
    name: str = ""
    merge: Callable[[Any, Any], Any] | None = None  # Only used with CUSTOM


class StackingCore[InputT, ResultT]:
    """
    Generic attribute-based configuration accumulator.

    Example:
        core = StackingCore(
            layers=[COLORS, MODIFIERS],
            finalizer=apply_color_and_modifiers,
        )
        result = core.bold.red("Hello")
    """

    __slots__ = ("_layers", "_state", "_finalizer")

    def __init__(
        self,
        layers: Sequence[Layer | Mapping[str, Any]],
        finalizer: Callable[[list[Any], InputT], ResultT],
        state: list[Any] | None = None,
    ) -> None:
        self._layers: list[Layer] = [
            layer if isinstance(layer, Layer) else Layer(mapping=layer)
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
                case LayerMode.REPLACE:
                    new_state[i] = value
                case LayerMode.ACCUMULATE:
                    current = new_state[i]
                    if current is None:
                        new_state[i] = (value,)
                    else:
                        new_state[i] = current + (value,)
                case LayerMode.CUSTOM:
                    if layer.merge is None:
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


#  LINE: -- string pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def compose_transforms(selections: list[Any], text: str) -> str:
    result = text
    for fn in selections:
        if fn is not None:
            result = fn(result)
    return result


pipeline = StackingCore(
    layers=[normalizers, sanitizers, formatters],
    finalizer=compose_transforms,
)

clean = pipeline.strip.html.title("  <b>hello</b>  ")


#  LINE: -- ColorStack -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass
class ColorConfig:
    color: str | None = None
    modifiers: tuple[str, ...] = ()


def color_finalizer(state: list[Any], text: str) -> str:
    color, modifiers = state
    # ... apply logic
    return formatted


ColorStack = StackingCore(
    layers=[
        Layer(ANSI_COLORS, mode=LayerMode.REPLACE, name="color"),
        Layer(ANSI_MODIFIERS, mode=LayerMode.ACCUMULATE, name="modifiers"),
    ],
    finalizer=color_finalizer,
)

#  LINE: -- Proxy -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class StackedMethod[InputT, ResultT]:
    # EXTRACT:
    """Wraps a StackingCore and optionally a base callable."""

    def __init__(
        self,
        stack: StackingCore[InputT, ResultT],
        base: Callable[[ResultT], Any] | None = None,
    ):
        self._stack = stack
        self._base = base

    def __getattr__(self, name: str) -> Self:
        return type(self)(getattr(self._stack, name), self._base)

    def __call__(self, arg: InputT) -> Any:
        result = self._stack(arg)
        return self._base(result) if self._base else result


# Usage
printer = Printer()
printer.header = StackedMethod(color_stack, base=print)
printer.header.bold.red("Important")


#  LINE: -- Composition -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ColorBox:
    def __init__(self):
        self._color_core = create_color_core()

    @property
    def color(self) -> StackingCore[str, str]:
        return self._color_core.clone()

    def print(self, text: str, **kwargs):
        colored = self._color_core.clone()(text)
        print(colored)


#  LINE: -- Narrowing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ContextualStack[InputT, ResultT](StackingCore[InputT, ResultT]):
    def __getattr__(self, name: str) -> Self:
        # ... existing logic ...
        new = super().__getattr__(name)

        # Example: after selecting "header", only allow certain colors
        if name == "header":
            # Return a restricted view
            return new.with_restricted_layers(...)
        return new


#  LINE: -- String Pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class TextProcessor:
    def __init__(self, color_box):
        self.sanitize = StackingCore(
            layers=[sanitizers, normalizers],
            finalizer=compose,
        )
        self.format = StackingCore(
            layers=[formatters],
            finalizer=apply_formatters,
        )
        self.color = color_box.color  # reuse existing ColorStack

    def process(self, text: str) -> str:
        text = self.sanitize.strip.html(text)
        text = self.format.title(text)
        return self.color.red.bold(text)
