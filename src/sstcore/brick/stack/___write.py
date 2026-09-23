"""
IMPLEMENT STUB FILE WRITER HERE

- Temporary until ready to move to proper place

"""

import dataclasses
import inspect
import itertools
from collections.abc import Mapping
from inspect import Signature
from pathlib import Path
from typing import Any

from . import ___data as data

#  LINE: -- Paths -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def local_stub_file() -> Path:
    return stub_file(file=Path(__file__))


def local_stub_dir_file() -> Path:
    return stub_dir_file(file=Path(__file__))


def stub_file(file: Path, extension: str = "_stub") -> Path:  # TODO: PathGuard
    name = f"{file.stem}{extension}.pyi"
    return file.parent / name


def stub_dir_file(file: Path, dir: str = "_stub") -> Path:  # TODO: PathGuard
    name = f"{file.stem}.pyi"
    return file.parent / dir / name


#  LINE: -- Writer -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def write_stub_for_colors():
    schema: dict[str, list[str]] = {
        "colors": list(data.ANSI_COLORS.keys()),
        "modifiers": list(data.ANSI_MODIFIERS.keys()),
    }

    stub_code = generate_fluent_stubs(
        class_prefix="Printer",
        group_mappings=schema,
        call_signature="def __call__(self, text: str) -> str: ...",
    )

    with open(local_stub_dir_file(), "w") as f:
        f.write(stub_code)

    print(f"Stub written to: {stub_file}")


#  LINE: -- Generic -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def generate_flat_stub(
    cls_name: str,
    registry: dict[str, Any],
    executor_signature: Signature,
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


def generate_fluent_stubs(  # AI: so far the best result
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


#  LINE: -- example classmethod -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclasses.dataclass(frozen=True)
class StackingCore:
    """Immutable fluent accumulator. Subclass, declare layer fields, implement apply."""

    _stack_index: Any

    @classmethod
    def generate_stub(cls) -> str:
        """Stub pyi body: explicit properties so the IDE can autocomplete keys."""

        # EXTRACT:
        cls_name = cls.__name__
        lines = [f"class {cls_name}:"]
        if dataclasses.is_dataclass(cls):
            for f in dataclasses.fields(cls):
                if f.name.startswith("_"):
                    continue
                anno = getattr(f.type, "__name__", repr(f.type))
                lines.append(f"    {f.name}: {anno}")
        if callable(cls):
            try:
                sig = inspect.signature(cls.__call__)
                lines.append(f"    def __call__{sig}: ...")
            except TypeError, ValueError:
                lines.append("    def __call__(self, *args, **kwargs): ...")
        for key in sorted(cls._stack_index):
            lines.append("    @property")
            lines.append(f"    def {key}(self) -> {cls_name}: ...")
        if len(lines) == 1:
            lines.append("    ...")
        return "\n".join(lines) + "\n"
