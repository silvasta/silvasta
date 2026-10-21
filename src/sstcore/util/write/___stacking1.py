"""
Generate the Stub Files for the Stacking

uv run -m sstcore.util.write._stacking

"""

__all__: list[str] = [
    "StubTyper",
]

import inspect
import itertools
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING

from ...brick.labor import funcname
from ...port.shape import Typer
from ...port.stacking import StackingCore

# def main():
# TASK:
# - paths by Stuby
# - stack by typer
# - launch from module?
# -> cli
#     """Launch full Pipeline for all 3 Examples"""
#     pairs: list[tuple[str, StackingCore]] = [
#         ("Random", DTO_STACK),
#         ("Ansi", ANSI_STACK),
#         ("Text", STRING_STACK),
#     ]
#     for name, core in pairs:
#         stub_file: str = StubTyper.draw(name, core)
#         target: Path = Config.target_file(name)
#         if Config.dry_run():
#             target.write_text(data=stub_file)
#             print(f"Successfully generated stubs at {target}")
#         else:
#             print(stub_file)
#             print(f"Successfully generated stub, No write to:\n{target}")


class StubTyper:
    """Smart Generator acting as the Single Source of Truth."""

    @classmethod
    def draw(cls, name: str, core: StackingCore) -> str:
        """Dynamically extract schema and signature from runtime Core"""

        return cls._generate_fluent_stubs(
            class_prefix=name,
            group_mappings=core.schema(),
            call_signature=cls._extract_signature(core.call),
        )

    @staticmethod
    def _generate_fluent_stubs(
        class_prefix: str,
        group_mappings: Mapping[str, list[str]],
        call_signature: str,
    ) -> str:
        groups: list[str] = sorted(group_mappings.keys())
        power_set: list[frozenset[str]] = StubTyper._generate_power_set(groups)

        stub_lines: list[str] = []

        for current_state in power_set:
            class_name: str = StubTyper._generate_class_name(
                current_state, class_prefix
            )
            stub_lines.append(f"class {class_name}:")

            available_groups = set(groups) - current_state
            has_methods = False

            for group in sorted(available_groups):
                next_state: frozenset[str] = current_state | {group}
                next_class_name: str = StubTyper._generate_class_name(
                    next_state, class_prefix
                )
                for attr in group_mappings[group]:
                    stub_lines.append("    @property")
                    stub_lines.append(
                        f"    def {attr}(self) -> {next_class_name}: ..."
                    )
                    has_methods = True

            stub_lines.append(f"    {call_signature}")
            if not has_methods:
                stub_lines.append("    pass")  # LATER: or: ... ?
            stub_lines.append("")

        return "\n".join(stub_lines)

    @staticmethod
    def _extract_signature(func: Callable) -> str:
        # EXTRACT: useful for other Typers, maybe brick.labor.detect
        """Extract typed signature, removing the internal 'state' dictionary."""

        sig: inspect.Signature = inspect.signature(func)
        parameters: list[inspect.Parameter] = list(sig.parameters.values())

        if parameters and parameters[0].name == "state":
            parameters.pop(0)

        params_str: list[str] = [
            "self",
            *[StubTyper._render_param(param) for param in parameters],
        ]
        return_type: str = (
            f": {(funcname(annot, default=str(annot)))}"
            if (annot := sig.return_annotation) != inspect.Signature.empty
            else "Any"
        )
        return f"def __call__({', '.join(params_str)}) -> {return_type}: ..."

    @staticmethod
    def _render_param(param: inspect.Parameter) -> str:
        param_def = f"{param.name}"
        if (annot := param.annotation) != inspect.Parameter.empty:
            # WARN: funcname checks the following:
            # attrs: Sequence[str] = ("__name__", "__qualname__")
            # - no issue because of __qualname__?
            param_def += f": {(funcname(annot, default=str(annot)))}"
        if param.default != inspect.Parameter.empty:
            param_def += f" = {repr(param.default)}"
        return param_def

    @staticmethod
    def _generate_power_set(groups: list[str]) -> list[frozenset[str]]:
        return [
            frozenset(combo)
            for i in range(len(groups) + 1)
            for combo in itertools.combinations(groups, i)
        ]

    @staticmethod
    def _generate_class_name(state: frozenset[str], class_prefix: str) -> str:
        if not state:
            return f"{class_prefix}Empty"
        return f"{class_prefix}" + "".join(
            sorted(s.capitalize() for s in state)
        )


if TYPE_CHECKING:
    _unit: Typer = StubTyper()
    _cls: type[Typer] = StubTyper

# if __name__ == "__main__":
#     main()
