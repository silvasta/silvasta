"""
Central hub for all stub generation.

Run with: uv run -m sstcore.util.write.stub
"""

from typing import Protocol

import importlib
import inspect
import itertools
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, TYPE_CHECKING

from ...brick.labor import funcname
from ...port.shape import Typer
from ...port.stacking import StackingCore
from ...util.path.guard import PathGuard   # your existing tool
from ...brick.time import day_count_plus


class StubGenerator(Protocol):
    """All future stub generators implement this."""
    @classmethod
    def draw(cls, name: str, source: Any, **kwargs: Any) -> str: ...
    @classmethod
    def write_for(cls, name: str, source: Any, target_package: Any, **kwargs: Any) -> Path: ...


class StackStubGenerator:
    """First real implementation — for fluent stacking APIs."""

    @classmethod
    def draw(cls, name: str, core: StackingCore, **kwargs: Any) -> str:
        return cls._generate_fluent_stubs(
            class_prefix=name,
            group_mappings=core.schema(),          # added to StackCore (see below)
            call_signature=cls._extract_signature(core.call),
        )

    @classmethod
    def write_for(
        cls,
        name: str,
        core: StackingCore,
        target_package: Any,          # str | ModuleType | Path
        subdir: str = "_stubs",
        dry_run: bool = False,
        **kwargs: Any,
    ) -> Path:
        """Robust write using PathGuard."""
        stub_dir = resolve_stub_dir(target_package, subdir=subdir)
        content = cls.draw(name, core, **kwargs)

        header = f"""# Auto-generated from StackStubGenerator on {day_count_plus()}.
# Source: {core.name if hasattr(core, 'name') else type(core).__name__}
# DO NOT EDIT. Change the StackDefinition / layers instead.

\"\"\"Fluent interface stubs for {name}.\"\"\"
from __future__ import annotations
from typing import Any
"""

        full_content = header + "\n\n" + content
        target_file = stub_dir / f"_{name.lower()}.pyi"

        if dry_run:
            print(f"DRY-RUN: would write to {target_file}")
            print(full_content[:500] + "\n...")
            return target_file

        with PathGuard(target_file, ensure_parent=True, backup=True):
            target_file.write_text(full_content, encoding="utf-8")
        print(f"✓ Wrote stub: {target_file}")
        return target_file

    @staticmethod
    def _generate_fluent_stubs(...) -> str:
        # Your original logic (cleaned up — sorted keys, better class naming if desired)
        # I kept the power-set of *layers* (Repeats/Greeting/Formatter) because it correctly models SINGLE vs MULTI locking.
        groups = sorted(group_mappings.keys())
        power_set = [
            frozenset(combo)
            for r in range(len(groups) + 1)
            for combo in itertools.combinations(groups, r)
        ]

        lines: list[str] = []
        for current in power_set:
            cls_name = _generate_class_name(current, class_prefix)
            lines.append(f"class {cls_name}:")

            available = set(groups) - set(current)
            has_props = False
            for g in sorted(available):
                next_state = current | {g}
                next_cls = _generate_class_name(next_state, class_prefix)
                for attr in sorted(group_mappings[g]):   # deterministic order
                    lines.append("    @property")
                    lines.append(f"    def {attr}(self) -> {next_cls}: ...")
                    has_props = True

            lines.append(f"    {call_signature}")
            if not has_props:
                lines.append("    pass")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def _extract_signature(func: Callable) -> str:
        """Fixed — no more '-> : str:' bug."""
        sig = inspect.signature(func)
        params = list(sig.parameters.values())

        # Drop internal 'state' parameter (the applicator always receives Accumulated first)
        if params and params[0].name in ("state", "self_state", "accumulated"):
            params = params[1:]

        param_strings = ["self"]
        for p in params:
            param_strings.append(_render_param(p))

        ret = "Any"
        if (annot := sig.return_annotation) != inspect.Signature.empty:
            ret = funcname(annot, default=str(annot))

        return f"def __call__({', '.join(param_strings)}) -> {ret}: ..."

    @staticmethod
    def _render_param(param: inspect.Parameter) -> str:
        parts = [param.name]
        if param.annotation is not inspect.Parameter.empty:
            ann = funcname(param.annotation, default=str(param.annotation))
            parts.append(f": {ann}")
        if param.default is not inspect.Parameter.empty:
            parts.append(f" = {repr(param.default)}")
        return "".join(parts)


# Central orchestration (easy to call from console.tools later)
def generate_stubs_for_package(target_package: Any = "sstcore.brick.stack", dry_run: bool = False) -> list[Path]:
    """One place to control all stub generation for a package."""
    from ...brick.stack import ANSI_STACK, DTO_STACK, STRING_STACK

    generator = StackStubGenerator
    paths = []
    paths.append(generator.write_for("Greeter", DTO_STACK, target_package, dry_run=dry_run))
    paths.append(generator.write_for("Printer", ANSI_STACK, target_package, dry_run=dry_run))
    paths.append(generator.write_for("Text", STRING_STACK, target_package, dry_run=dry_run))
    return paths


if __name__ == "__main__":
    import sstcore.brick.stack as stack_pkg
    generate_stubs_for_package(stack_pkg, dry_run=False)


if TYPE_CHECKING:
    _unit: Typer = StackStubGenerator()
    _cls: type[Typer] = StackStubGenerator
