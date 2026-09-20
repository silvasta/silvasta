"""
Frozen DataClass Version

-
"""

from pathlib import Path

__all__: list[str] = [
    "StackingCore",
]


import itertools
import string
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Self

WRITE_STUB = True
WRITE_STUB = False
stem = f"{Path(__file__).stem}_stub"
stub_file: Path = Path(f"{__file__}i").with_stem(stem)

type AttrRegistry = Mapping[str, tuple[str, Any]]
type StateDict = Mapping[str, Any]


@dataclass(frozen=True)
class StackingCore[R]:
    _registry: AttrRegistry
    _executor: Callable[[StateDict, tuple[Any, ...], dict[str, Any]], R]
    _state: StateDict = field(default_factory=dict)

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

    def __call__(self, *args: Any, **kwargs: Any) -> R:
        """Pass the accumulated state and all runtime arguments to the executor."""
        return self._executor(self._state, args, kwargs)

    @classmethod
    def build(
        cls,
        mappings: Mapping[str, Mapping[str, Any]],
        executor: Callable[[StateDict, tuple[Any, ...], dict[str, Any]], R],
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


#  LINE: -- terminal -- -- - -- -- - -- -- - -- -- - -- -- - -- --


ANSI_COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
}
ANSI_MODIFIERS = {
    "bold": "\033[1m",
    "underline": "\033[4m",
}


def terminal_executor(
    state: StateDict, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:

    color: str = state.get("colors", "")
    modifier: str = state.get("modifiers", "")
    reset: str = "\033[0m" if color or modifier else ""

    target: str = args[0] if args else kwargs.get("text", "")

    return f"{modifier}{color}{target}{reset}"


printer: StackingCore[str] = StackingCore.build(
    mappings={"colors": ANSI_COLORS, "modifiers": ANSI_MODIFIERS},
    executor=terminal_executor,
)

print(printer.bold.green("Hello World"))
print(printer.red.underline("bye"))


#  LINE: -- sanitize -- -- - -- -- - -- -- - -- -- - -- -- - -- --


STRING_NORMALIZERS = {
    "lower": str.lower,
    "upper": str.upper,
}
STRING_SANITIZERS = {
    "strip_punct": lambda s: s.translate(
        str.maketrans("", "", string.punctuation)
    ),
    "trim": str.strip,
}


def string_pipeline_executor(
    state: StateDict, args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:
    text = args[0]

    # Apply in deterministic order regardless of access order
    if "normalize" in state:
        text = state["normalize"](text)
    if "sanitize" in state:
        text = state["sanitize"](text)

    return text


string_formatter = StackingCore.build(
    mappings={"normalize": STRING_NORMALIZERS, "sanitize": STRING_SANITIZERS},
    executor=string_pipeline_executor,
)

# Usage
clean: str = string_formatter.strip_punct.lower("HELLO, World!! ")
print(clean)


def generate_fluent_stubs(
    class_prefix: str,
    group_mappings: Mapping[str, list[str]],
    call_signature: str = "def __call__(self, text: str) -> str: ...",
) -> str:
    """Generates .pyi stub string for a fluent builder state machine"""

    groups = sorted(group_mappings.keys())
    # stub_lines = ["from typing import Any", ""]
    stub_lines = []

    # Generate the power set of all group combinations (the "states")
    power_set = []
    for i in range(len(groups) + 1):
        for combo in itertools.combinations(groups, i):
            power_set.append(frozenset(combo))

    def get_class_name(state: frozenset[str]) -> str:
        if not state:
            return f"{class_prefix}Empty"
        return f"{class_prefix}" + "".join(
            sorted(s.capitalize() for s in state)
        )

    # Generate a class for each state
    for current_state in power_set:
        class_name = get_class_name(current_state)
        stub_lines.append(f"class {class_name}:")

        # Add properties for groups NOT yet in the current state
        available_groups = set(groups) - current_state
        has_methods = False

        for group in sorted(available_groups):
            # The future state if an attribute from this group is accessed
            next_state = current_state | {group}
            next_class_name = get_class_name(next_state)

            for attr in group_mappings[group]:
                stub_lines.append("    @property")
                stub_lines.append(
                    f"    def {attr}(self) -> {next_class_name}: ..."
                )
                has_methods = True

        # Every state needs the execution method
        stub_lines.append(f"    {call_signature}")
        if not has_methods:
            stub_lines.append("    pass")

        stub_lines.append("")

    return "\n".join(stub_lines)


def write_stub():
    schema: dict[str, list[str]] = {
        "colors": list(ANSI_COLORS.keys()),
        "modifiers": list(ANSI_MODIFIERS.keys()),
    }

    stub_code = generate_fluent_stubs(
        class_prefix="Printer",
        group_mappings=schema,
        call_signature="def __call__(self, text: str) -> str: ...",
    )

    with open(stub_file, "w") as f:
        f.write(stub_code)

    print(f"Stub written to: {stub_file}")


if TYPE_CHECKING:
    from ._core1_stub import PrinterEmpty


printer: PrinterEmpty = StackingCore.build(  # ty:ignore
    mappings={"colors": ANSI_COLORS, "modifiers": ANSI_MODIFIERS},
    executor=terminal_executor,
)

print(printer.blue.bold("it works? "))
print(printer.underline.red("where is the line?"))

if __name__ == "__main__":
    if WRITE_STUB:
        write_stub()
