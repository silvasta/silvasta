"""
DERIVE EXAMPLE USAGE HERE

- Temporary until ready to move to proper place

"""

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from . import ___data as data
from . import ___define as port
from . import ___stack as stack

#  LINE: -- Terminal -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def terminal_executor(
    state: port.StateDict, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:

    color: str = state.get("colors", "")
    modifier: str = state.get("modifiers", "")
    reset: str = data.ANSI_RESET if color or modifier else ""

    target: str = args[0] if args else kwargs.get("text", "")

    return f"{modifier}{color}{target}{reset}"


printer: stack.StackCore1[str] = stack.StackCore1.build(
    mappings={"colors": data.ANSI_COLORS, "modifiers": data.ANSI_MODIFIERS},
    executor=terminal_executor,
)

print(printer.bold.green("Hello World"))
print(printer.red.underline("bye"))


#  LINE: -- String -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def string_pipeline_executor(
    state: port.StateDict, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:
    text = args[0]

    # Apply in deterministic order regardless of access order
    if "normalize" in state:
        text = state["normalize"](text)
    if "sanitize" in state:
        text = state["sanitize"](text)

    return text


string_formatter = stack.StackCore1.build(
    mappings={
        "normalize": data.STRING_NORMALIZERS,
        "sanitize": data.STRING_SANITIZERS,
    },
    executor=string_pipeline_executor,
)

# Usage
clean: str = string_formatter.strip_punct.lower("HELLO, World!! ")
print(clean)

if TYPE_CHECKING:
    from ._core1_stub1 import PrinterEmpty


printer: PrinterEmpty = stack.StackCore1.build(
    mappings={"colors": data.ANSI_COLORS, "modifiers": data.ANSI_MODIFIERS},
    executor=terminal_executor,
)

print(printer.blue.bold("it works? "))
print(printer.underline.red("where is the line?"))


#  LINE: -- string pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def compose_transforms(selections: list[Any], text: str) -> str:
    result = text
    for fn in selections:
        if fn is not None:
            result = fn(result)
    return result


pipeline = stack.StackCore2(
    layers=[data.STRING_NORMALIZERS, data.STRING_SANITIZERS],
    finalizer=compose_transforms,
)

clean = pipeline.strip.html.title("  <b>hello</b>  ")


#  LINE: -- Stack2 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class StackedMethod[InputT, ResultT]:
    """Wraps a StackingCore and optionally a base callable."""

    def __init__(
        self,
        stack: stack.StackCore2[InputT, ResultT],
        base: Callable[[ResultT], Any] | None = None,
    ):
        self._stack = stack
        self._base = base

    def __getattr__(self, name: str) -> Self:
        return type(self)(getattr(self._stack, name), self._base)

    def __call__(self, arg: InputT) -> Any:
        result = self._stack(arg)
        return self._base(result) if self._base else result


@dataclass
class ColorConfig:
    color: str | None = None
    modifiers: tuple[str, ...] = ()


def color_finalizer(state: list[Any], text: str) -> str:
    raise NotImplementedError


ColorStack2 = stack.StackCore2(
    layers=[
        stack.Layer2(
            data.ANSI_COLORS,
            mode=port.LayerMode.REPLACE,
            name="color",
        ),
        stack.Layer2(
            data.ANSI_MODIFIERS,
            mode=port.LayerMode.ACCUMULATE,
            name="modifiers",
        ),
    ],
    finalizer=color_finalizer,
)


class ColorBox:
    def __init__(self):
        self._color_core = ColorStack2

    @property
    def color(self) -> stack.StackCore2[str, str]:
        return self._color_core.clone()

    def print(self, text: str, **kwargs):
        colored = self._color_core.clone()(text)
        print(colored)


#  LINE: -- Stack3 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# 1. Define the Immutable State
@dataclass(frozen=True)
class ColorContext:
    color: str | None = None
    modifiers: tuple[str, ...] = ()


# 2. Define Mutators (How attributes change the state)
def set_color(c: str) -> port.Mutator[ColorContext]:
    return lambda ctx: dataclasses.replace(ctx, color=c)


def add_modifier(m: str) -> port.Mutator[ColorContext]:
    return lambda ctx: dataclasses.replace(ctx, modifiers=ctx.modifiers + (m,))


# 3. Build the Registry from your mappings
COLOR_REGISTRY: dict[str, port.Mutator[ColorContext]] = {
    "red": set_color("\033[31m"),
    "green": set_color("\033[32m"),
    "bold": add_modifier("\033[1m"),
    "underline": add_modifier("\033[4m"),
}


# 4. Define the Execution Logic
def color_executor(ctx: ColorContext, text: str) -> str:
    codes = list(ctx.modifiers)
    if ctx.color:
        # Simplified for example
        clean_code = ctx.color[2:-1]
        codes.append(clean_code)

    if not codes:
        return text

    prefix = f"\033[{';'.join(codes)}m"
    return f"{prefix}{text}\033[0m"


color_printer = stack.StackCore3(
    context=ColorContext(), registry=COLOR_REGISTRY, executor=color_executor
)
print(color_printer.bold.green.underline("Hello Peter"))


@dataclass(frozen=True)
class StringPipelineContext:
    operations: tuple[Callable[[str], str], ...] = ()


def add_op(op: Callable[[str], str]) -> port.Mutator[StringPipelineContext]:
    return lambda ctx: dataclasses.replace(
        ctx, operations=ctx.operations + (op,)
    )


PIPELINE_REGISTRY = {
    "lower": add_op(str.lower),
    "strip": add_op(str.strip),
    "sanitize": add_op(lambda s: s.replace("<script>", "")),
}


def pipeline_executor(ctx: StringPipelineContext, text: str) -> str:
    result = text
    for op in ctx.operations:
        result = op(result)
    return result


stringer = stack.StackCore3(
    context=StringPipelineContext(),
    registry=PIPELINE_REGISTRY,
    executor=pipeline_executor,
)
clean_text = stringer.strip.lower.sanitize("   <script>Alert</script>   ")


#  LINE: -- Stack3 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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
    "repeats": stack.AttrGroup(data.ATTR1, default=1),
    "greeting": stack.AttrGroup(data.ATTR2),
    "formatter": stack.AttrGroup(data.ATTR3),
}

Stack3 = stack.StackCore4.create("Stack", groups, dto_applicator)
handler = type("Handler", (), {"stack": Stack3()})()

x3 = handler.stack.key11.key21.key31("Alice")
y3 = handler.stack.key21.key32("Bob")
z3 = handler.stack.key13.key33("Charlie")


def color_applicator(state: dict, text: str, context: Any = None) -> str:
    # Reuse your existing ANSI / Rich logic here, reading state["color"], state.get("modifiers", ())
    formatted_text = "" or text
    ...
    if not formatted_text:
        raise NotImplementedError
    return formatted_text


color_groups = {
    "color": stack.AttrGroup(
        data.ANSI_COLORS,
        resolver=lambda n, context: context.get(n) if context else None,
    ),
    "modifiers": stack.AttrGroup(
        data.ANSI_MODIFIERS, default=(), strategy="append"
    ),
}

ColorStack4 = stack.StackCore4.create(
    "ColorStack4", color_groups, color_applicator, {"modifiers": ()}
)


def pipeline_applicator(state: dict, text: str, context: Any = None) -> str:
    result = text
    for transform in state.get("transforms", ()):
        result = transform(result)
    return result


_sanitizers = data.STRING_SANITIZERS
_normalizers = data.STRING_NORMALIZERS
_formatters = data.ATTR3
_colorizers = data.ANSI_COLORS

pipeline_groups = {
    "transforms": stack.AttrGroup(
        {
            **_sanitizers,
            **_normalizers,
            **_formatters,
            **_colorizers,
        },
        default=(),
        strategy="append",
    )
}

StringPipeline = stack.StackCore4.create(
    "StringPipeline", pipeline_groups, pipeline_applicator
)
clean = StringPipeline().strip.lower.capitalize  # accumulates transforms
print(clean("  Hello WORLD!  "))
