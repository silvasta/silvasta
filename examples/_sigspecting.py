"""
Showcase script for SigSpec, LspViolation evaluation, Capability Algebra, and Format Renderings.

Run with:
    python examples/demo_sigspec_lsp.py
"""

from typing import Any

from sstcore.brick.call.lsp import SigSpec
from sstcore.port.sigspect import LspViolation


def main():
    demo_single_spec_views()
    demo_format_mini_language()
    demo_composite_violations()
    demo_algebra()
    demo_rich_panel()
    pass


# ----------------------------------------------------------------------------
# 1. Sample Callables
# ----------------------------------------------------------------------------
def baseline_handler(
    user_id: int | str,
    /,
    action: str = "read",
    *,
    timeout: float = 5.0,
    **extra: Any,
) -> dict[str, Any]:
    return {"user": user_id, "action": action}


def valid_replacement(
    uid: int | str | bytes,
    /,
    action: str = "read",
    extra_pos: int = 0,
    *args: Any,
    timeout: float = 5.0,
    **extra: Any,
) -> dict[str, str]:
    return {"user": str(uid), "action": action}


def broken_replacement(
    uid: int,  # Renamed pos-only + narrowed (int|str -> int)
    action: str,  # Lost default -> INCREASED_MIN_POS
    *,
    force: bool,  # Added required kw -> ADDED_REQUIRED_KW
) -> list[str]:  # Dropped **extra + disjoint return (dict -> list)
    return [str(uid), action]


# ----------------------------------------------------------------------------
# 2. Run Demos
# ----------------------------------------------------------------------------
def demo_single_spec_views() -> None:
    section("1. SigSpec Inspection & Single-Spec Views")
    spec = SigSpec.detect(baseline_handler)
    print("Target         : baseline_handler")
    print(f"Positionals    : {[str(p) for p in spec.positionals]}")
    print(
        f"Keyword Map    : { {k: str(v) for k, v in spec.keyword_map.items()} }"
    )
    print(
        f"Min/Max Pos    : min={spec.min_positional}, max={spec.max_positional}"
    )
    print(f"Required       : {[p.name for p in spec.required]}")
    print(
        f"VarArgs/Kwargs : *args={spec.has_var_positional}, **kwargs={spec.has_var_keyword}"
    )
    print(f"Return Type    : {spec.result}")


def demo_format_mini_language() -> None:
    section("2. LspViolation Format Mini-Language Showcase")
    single = LspViolation.NARROWED_PARAM_TYPE

    specs = [
        ("", "str(flag) default"),
        ("b", "Bit representation (:b)"),
        ("t", "Title only (:t)"),
        ("e", "Extended detail only (:e)"),
        ("v", "Verbose single-line (:v)"),
        ("v; ==> ", "Verbose custom separator (:v; ==> )"),
        ("i", "Icon-boxed title (:i)"),
        ("iv", "Icon-boxed verbose (:iv)"),
        ("vn", "Verbose multiline (:vn)"),
        ("ivn", "Icon-boxed multiline (:ivn)"),
    ]

    for fmt, label in specs:
        rendered = format(single, fmt)
        sep = "\n" if "\n" in rendered else " "
        print(f"• {label:<36} ->{sep}{rendered}")


def demo_composite_violations() -> None:
    section("3. Composite Violation Evaluation & Preset Tolerance")
    s_base = SigSpec.detect(baseline_handler)
    s_valid = SigSpec.detect(valid_replacement)
    s_broken = SigSpec.detect(broken_replacement)

    v_valid = s_base.diff(s_valid)
    print(f"baseline -> valid_replacement  : {v_valid}")
    print(f"  Strictly allowed (ZERO)?     : {s_base.allows(s_valid)}")
    print(
        f"  Allowed with POS_ONLY_RENAMED: {s_base.allows(s_valid, tolerance=LspViolation.POS_ONLY_RENAMED)}"
    )
    print(f"  Explanation (:iv)            : {v_valid:iv}\n")

    v_broken = s_base.diff(s_broken)
    print(f"baseline -> broken_replacement : {v_broken}")
    print(f"  Bitmask (:b)                 : {v_broken:b}")
    print(f"  Collapsed summary (:t)       : {v_broken:t}")
    print(f"\n  Full Multiline Breakdown (:ivn):\n{v_broken:ivn}")


def demo_algebra() -> None:
    section("4. Structural Capability Set Algebra (-, &, |)")

    def reader(path: str, mode: str = "r", *, encoding: str = "utf-8") -> str:
        return ""

    def writer(path: str, *, mode: str = "w", atomic: bool = True) -> bytes:
        return b""

    s_read = SigSpec.detect(reader)
    s_write = SigSpec.detect(writer)

    s_and = s_read & s_write
    s_sub = s_read - s_write
    s_or = s_read | s_write

    def _summarize(label: str, s: SigSpec) -> None:
        print(
            f"{label:<16} | pos={[p.name for p in s.pos]} "
            f"both={[p.name for p in s.both]} "
            f"key={[p.name for p in s.key]} "
            f"-> {s.result}"
        )

    _summarize("reader", s_read)
    _summarize("writer", s_write)
    print("-" * 78)
    _summarize("reader & writer", s_and)
    _summarize("reader - writer", s_sub)
    _summarize("reader | writer", s_or)


def demo_rich_panel() -> None:
    from rich.console import Console

    section("5. Rich Panel Rendering (__rich__)")
    console = Console()
    s_base = SigSpec.detect(baseline_handler)
    s_broken = SigSpec.detect(broken_replacement)
    console.print(s_base.diff(s_broken))


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n  {title}\n{'=' * 78}")


if __name__ == "__main__":
    main()
