from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, Self, cast

from .___data import ANSI_COLORS, ANSI_MODIFIERS, ATTR1, ATTR2, ATTR3


class Applicator[InputT, OutputT](Protocol):
    """Final logic: takes accumulated state + input → result."""

    def __call__(
        self, state: dict[str, Any], value: InputT, context: Any | None = None
    ) -> OutputT: ...


@dataclass
class AttrGroup[T]:
    """One dimension of configuration (e.g. colors, modifiers, pipeline steps)."""

    mapping: dict[str, T]
    default: T | None = None
    strategy: str = "set"  # "set" | "append" | "extend"
    # Optional dynamic resolver (e.g. lookup in ColorBox)
    resolver: Callable[[str, dict[str, T]], Any] | None = None


class StackingCore[InputT, OutputT]:
    """Generalized fluent stacking core.

    Created via the `.create()` factory (recommended) or subclassed.
    Supports different update strategies per group and context injection.
    """

    # Set by factory or on subclass
    _groups: dict[str, AttrGroup] = {}
    _applicator: Applicator[InputT, OutputT] | None = None
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
        applicator: Applicator[InputT, OutputT],
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


#  LINE: -- DTO -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def dto_applicator(
    state: dict[str, Any], target: str, context: Any = None
) -> str:
    string = f"{target} says {state.get('greeting')} to Peter"
    for _ in range(state.get("repeats", 1)):
        print(string)
    if state.get("formatter"):
        string = state["formatter"](string)
    return string


groups = {
    "repeats": AttrGroup(ATTR1, default=1),
    "greeting": AttrGroup(ATTR2),
    "formatter": AttrGroup(ATTR3),
}

Stack = StackingCore.create("Stack", groups, dto_applicator)
handler = type("Handler", (), {"stack": Stack()})()

x = handler.stack.key11.key21.key31("Alice")
y = handler.stack.key21.key32("Bob")
z = handler.stack.key13.key33("Charlie")

#  LINE: -- ColorStack -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def color_applicator(state: dict, text: str, context: Any = None) -> str:
    # Reuse your existing ANSI / Rich logic here, reading state["color"], state.get("modifiers", ())
    formatted_text = "" or text
    ...
    if not formatted_text:
        raise NotImplementedError
    return formatted_text


color_groups = {
    "color": AttrGroup(
        ANSI_COLORS,
        resolver=lambda n, context: context.get(n) if context else None,
    ),
    "modifiers": AttrGroup(ANSI_MODIFIERS, default=(), strategy="append"),
}

ColorStack = StackingCore.create(
    "ColorStack", color_groups, color_applicator, {"modifiers": ()}
)

# In ColorBox / Printer:
# self.color = ColorStack(context=self)   # or .with_context(box_ref=self)

#  LINE: -- Format -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def pipeline_applicator(state: dict, text: str, context: Any = None) -> str:
    result = text
    for transform in state.get("transforms", ()):
        result = transform(result)
    return result


pipeline_groups = {
    "transforms": AttrGroup(
        {**sanitizers, **normalizers, **formatters, **colorizers},
        default=(),
        strategy="append",
    )
}

StringPipeline = StackingCore.create(
    "StringPipeline", pipeline_groups, pipeline_applicator
)
clean = StringPipeline().strip.lower.capitalize  # accumulates transforms
print(clean("  Hello WORLD!  "))
