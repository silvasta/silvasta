import inspect
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Any, Concatenate, ParamSpec, Self, TypeVar

# Type Variables for modern Generics
TContext = TypeVar("TContext")
TReturn = TypeVar("TReturn")
P = ParamSpec("P")

# A Mutator takes a context and returns an updated context
type Mutator[T] = Callable[[T], T]


class StackingCore[TContext, **P, TReturn]:
    """Strictly separates State Accumulation from Execution."""

    def __init__(
        self,
        context: TContext,
        registry: dict[str, Mutator[TContext]],
        executor: Callable[Concatenate[TContext, P], TReturn],
    ) -> None:
        self._context: TContext = context
        self._registry: dict[str, Mutator[TContext]] = registry
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


# ==========================================
# PYI STUB GENERATOR (The IDE Solution)
# ==========================================


def generate_stub(
    cls_name: str,
    registry: dict[str, Any],
    executor_signature: inspect.Signature,
    file_path: str,
) -> None:
    lines = [
        "from typing import Any, Callable",
        "from typing_extensions import Self",
        "",
        f"class {cls_name}:",
    ]

    # 1. Generate properties for autocomplete chaining
    for attr_name in registry.keys():
        lines.append("    @property")
        lines.append(f"    def {attr_name}(self) -> Self: ...")

    # 2. Generate the __call__ signature
    lines.append("")
    lines.append(f"    def __call__{executor_signature} -> Any: ...")

    with open(file_path, "w") as f:
        f.write("\n".join(lines))
        f.write("\n")


#  LINE: -- ColorStack -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# 1. Define the Immutable State
@dataclass(frozen=True)
class ColorContext:
    color: str | None = None
    modifiers: tuple[str, ...] = ()


# 2. Define Mutators (How attributes change the state)
def set_color(c: str) -> Mutator[ColorContext]:
    return lambda ctx: replace(ctx, color=c)


def add_modifier(m: str) -> Mutator[ColorContext]:
    return lambda ctx: replace(ctx, modifiers=ctx.modifiers + (m,))


# 3. Build the Registry from your mappings
COLOR_REGISTRY: dict[str, Mutator[ColorContext]] = {
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


# 5. Instantiate
printer = StackingCore(
    context=ColorContext(), registry=COLOR_REGISTRY, executor=color_executor
)

# USAGE:
print(printer.bold.green.underline("Hello Peter"))


#  LINE: -- Format -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class StringPipelineContext:
    operations: tuple[Callable[[str], str], ...] = ()


def add_op(op: Callable[[str], str]) -> Mutator[StringPipelineContext]:
    return lambda ctx: replace(ctx, operations=ctx.operations + (op,))


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


stringer = StackingCore(
    context=StringPipelineContext(),
    registry=PIPELINE_REGISTRY,
    executor=pipeline_executor,
)

# USAGE:
clean_text = stringer.strip.lower.sanitize("   <script>Alert</script>   ")
