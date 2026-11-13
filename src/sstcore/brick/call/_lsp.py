"""
Define the Rules and Classification of LSP Violations

-
"""

__all__: list[str] = [
    "LspViolation",
    "LspViolationDetails",
]


from enum import IntFlag, auto
from typing import Any, NamedTuple

from ...port._types import _Stringable
from ..format.name import ColoredName


class LspViolation(IntFlag):
    """
    Categorize different Kinds of LSP Violations

    - POS_ONLY_RENAMED: technically No Violation
    - HOOK_PLUGIN: Allow narrowing Variadic Hooks into concrete Parameter
    - SINK_CALLBACK: Ignore Return Value, optional Kwargs can be dropped

    """

    ZERO = 0

    # Positional
    POS_ONLY_RENAMED = auto()
    DROPPED_VAR_POS = auto()
    REDUCED_MAX_POS = auto()
    INCREASED_MIN_POS = auto()

    # Keyword / Binding Vectors
    DROPPED_VAR_KW = auto()
    LOST_KW_ACCESS = auto()
    LOST_POS_ACCESS = auto()
    DROPPED_KW_NAME = auto()
    ADDED_REQUIRED_KW = auto()

    # Parameter Types (Contravariance)
    ADDED_PARAM_CONSTRAINT = auto()
    NARROWED_PARAM_TYPE = auto()
    DISJOINT_PARAM_TYPE = auto()

    # Return Types (Covariance)
    WIDENED_RETURN_SUPERSET = auto()
    OVERLAPPING_RETURN_UNION = auto()
    DISJOINT_RETURN_TYPE = auto()

    # Execution Semantics
    SYNC_ASYNC_MISMATCH = auto()
    GENERATOR_MISMATCH = auto()
    DESCRIPTOR_BINDING_SHIFT = auto()

    HOOK_PLUGIN = (
        POS_ONLY_RENAMED
        | DROPPED_VAR_POS
        | DROPPED_VAR_KW
        | ADDED_PARAM_CONSTRAINT
    )

    SINK_CALLBACK = (
        POS_ONLY_RENAMED
        | DROPPED_VAR_POS
        | DROPPED_VAR_KW
        | DROPPED_KW_NAME
        | WIDENED_RETURN_SUPERSET
        | OVERLAPPING_RETURN_UNION
        | DISJOINT_RETURN_TYPE
    )

    MORPHING_INCLUSIVE = (  # Original return type remains
        POS_ONLY_RENAMED | ADDED_PARAM_CONSTRAINT | WIDENED_RETURN_SUPERSET
    )

    MORPHING_ANY_RETURN = (  # Full transformation
        MORPHING_INCLUSIVE | OVERLAPPING_RETURN_UNION | DISJOINT_RETURN_TYPE
    )

    @property
    def explain(self) -> LspViolationDetails:
        match self:
            case LspViolation.ZERO:
                return self._rule_ctor(
                    "No violation",
                    "Replacement signature is strictly LSP-compliant; not even positional-only parameter renaming is permitted.",
                )

            # Positional
            case LspViolation.POS_ONLY_RENAMED:
                return self._rule_ctor(
                    "Positional-only parameter renamed",
                    "Callers cannot pass positional-only parameters by keyword, so runtime calls never break, though strict reflection or stub checkers flag the name mismatch.",
                )
            case LspViolation.DROPPED_VAR_POS:
                return self._rule_ctor(
                    "Variadic positional absorption lost",
                    "Baseline promised infinite positional argument absorption via *args; replacement caps positional arity.",
                )
            case LspViolation.REDUCED_MAX_POS:
                return self._rule_ctor(
                    "Finite positional capacity reduced",
                    "Baseline accepted a larger finite number of positional arguments than replacement; fails when optional positional arguments are supplied.",
                )
            case LspViolation.INCREASED_MIN_POS:
                return self._rule_ctor(
                    "Minimum required positional arguments increased",
                    "Replacement demands more positional arguments than baseline's minimum (by removing a default or adding a required parameter).",
                )

            # Keyword / Binding Vectors
            case LspViolation.DROPPED_VAR_KW:
                return self._rule_ctor(
                    "Keyword absorption lost",
                    "Baseline absorbed arbitrary keyword arguments; replacement rejects unknown keys with TypeError.",
                )
            case LspViolation.LOST_KW_ACCESS:
                return self._rule_ctor(
                    "Keyword access vector removed",
                    "Parameter still exists at the same position, but changed from positional-or-keyword to positional-only (/); callers passing it by keyword fail with TypeError.",
                )
            case LspViolation.LOST_POS_ACCESS:
                return self._rule_ctor(
                    "Positional access vector removed",
                    "Parameter still exists with the same name, but changed from positional-or-keyword to keyword-only (*); callers passing it positionally fail with TypeError.",
                )
            case LspViolation.DROPPED_KW_NAME:
                return self._rule_ctor(
                    "Named keyword parameter removed",
                    "A specific keyword parameter accepted by baseline no longer exists and cannot be absorbed by **kwargs.",
                )
            case LspViolation.ADDED_REQUIRED_KW:
                return self._rule_ctor(
                    "Mandatory keyword parameter added",
                    "Replacement introduces a new keyword-only parameter without a default value; standard callers fail with TypeError.",
                )

            # Parameter Types (Contravariance)
            case LspViolation.ADDED_PARAM_CONSTRAINT:
                return self._rule_ctor(
                    "Parameter type annotation added",
                    "Baseline accepted Any (untyped), while replacement declares an explicit type constraint; safe in plain Python, fails under runtime type guards.",
                )
            case LspViolation.NARROWED_PARAM_TYPE:
                return self._rule_ctor(
                    "Parameter type narrowed (contravariance break)",
                    "Replacement accepts a strict subtype of baseline's input; fails whenever a valid supertype or union branch from baseline is passed.",
                )
            case LspViolation.DISJOINT_PARAM_TYPE:
                return self._rule_ctor(
                    "Incompatible parameter type",
                    "Replacement parameter type has zero overlap with baseline's parameter type; guaranteed failure for any valid baseline input.",
                )

            # Return Types (Covariance)
            case LspViolation.WIDENED_RETURN_SUPERSET:
                return self._rule_ctor(
                    "Return type widened to superset (covariance break)",
                    "Original return type remains included as a subtype or union member of the new return type; callers checking types dynamically can still handle it.",
                )
            case LspViolation.OVERLAPPING_RETURN_UNION:
                return self._rule_ctor(
                    "Return type partially shifted",
                    "Intersection exists between baseline and replacement return types, but some baseline return types disappear while unexpected new types appear.",
                )
            case LspViolation.DISJOINT_RETURN_TYPE:
                return self._rule_ctor(
                    "Incompatible return type",
                    "Replacement return type shares zero overlap with baseline's return type; safe only for sinks where the caller discards the return value.",
                )

            # Execution Semantics
            case LspViolation.SYNC_ASYNC_MISMATCH:
                return self._rule_ctor(
                    "Sync/async calling convention mismatch",
                    "Switching between def and async def breaks the coroutine protocol: sync callers receive an unawaited coroutine, or async callers fail awaiting a non-awaitable.",
                )
            case LspViolation.GENERATOR_MISMATCH:
                return self._rule_ctor(
                    "Generator/eager execution mismatch",
                    "Switching between a standard return and yield changes immediate execution into lazy iterator creation.",
                )
            case LspViolation.DESCRIPTOR_BINDING_SHIFT:
                return self._rule_ctor(
                    "Descriptor binding convention changed",
                    "Changing between bound method, @classmethod, and @staticmethod alters implicit receiver (self/cls) injection and shifts positional indices.",
                )

            case LspViolation.HOOK_PLUGIN:
                return self._rule_ctor(
                    "Plugin/hook extension preset",
                    "Allows narrowing open *args/**kwargs extension points into concrete typed parameters while permitting positional-only renames.",
                )
            case LspViolation.SINK_CALLBACK:
                return self._rule_ctor(
                    "Fire-and-forget sink callback preset",
                    "Ignores return type changes completely and allows dropping unused variadic or optional keyword arguments.",
                )
            case LspViolation.MORPHING_INCLUSIVE:
                return self._rule_ctor(
                    "Inclusive return-morphing preset",
                    "Allows widening the return type as long as the baseline return type remains a valid subtype or member of the new return contract.",
                )
            case LspViolation.MORPHING_ANY_RETURN:
                return self._rule_ctor(
                    "Unrestricted return-morphing preset",
                    "Allows replacing the return type with any type while preserving strict input call compatibility.",
                )

            case _:
                return self._merge(*(member.explain for member in self))

    def _rule_ctor(self, title: str, detail: str, /) -> LspViolationDetails:
        return LspViolationDetails(self, title, detail)

    def _merge(self, *rules: LspViolationDetails) -> LspViolationDetails:
        return self._rule_ctor(
            "\n".join(f"[{r.origin.value}] {r.title}" for r in rules),
            "\n".join(f"[{r.origin.value}] {r.detail}" for r in rules),
        )

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "" | "s":
                return str(self)
            case "b":
                return f"{self:0{len(type(self))}b}"
            case _:
                if (
                    any(c in format_spec for c in "<>^")
                    and format_spec[-1] not in "bcdoxXn"
                ):
                    return format(str(self), format_spec)
                return super().__format__(format_spec)

    def __str__(self) -> str:
        return _COLORED_LSP_NAME.raw(self._colored_name_args)

    def __rich__(self) -> str:
        return _COLORED_LSP_NAME.rich(self._colored_name_args)

    @property
    def _colored_name_args(self) -> list[_Stringable]:
        _name = type(self).__name__
        return [_name[:3], _name[3:], f"{self:b}", self.name, self.value]


def _get_pattern() -> str:
    cls1 = "[bold black on white]_{cls1}[/]"
    cls2 = "[bold red on white]{cls2}_[/]"
    bits = "[red]{bits}[/]"
    name = "[steel_blue1]{name}[/]"
    num_ = "[bold purple]{value}[/]"
    return f"{cls1}{cls2}[{bits}]::{name}[{num_}]"


_COLORED_LSP_NAME = ColoredName(_get_pattern())


class LspViolationDetails(NamedTuple):
    origin: Any  # CHECK: Any
    title: str
    detail: str = ""

    def __str__(self) -> str:
        return f"{self:s}"

    def __repr__(self) -> str:
        return f"{self}\n\n{self:d}" if self.detail else f"{self}"

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "" | "s":
                return self.title
            case "d":
                return self.detail
            case "r":
                return repr(self)
            case "o":
                return f"{self.origin}\n{self!r}"
            case _:
                return format(str(self), format_spec)

    def __rich__(self):
        from rich.console import Group
        from rich.panel import Panel

        # LATER: add __rich__ to LspViolation
        return Group(Panel(self.origin), Panel(repr(self)))


if __name__ == "__main__":
    from rich import print

    print()
    for violation in LspViolation:
        print(violation)
        print(str(violation))
        print()

    for violation in LspViolation:
        print(f"{violation}\n{violation.explain!r}")
        print()

    print()
    for violation in LspViolation:
        print(violation.explain)
        print()

    print("--- s")
    print()

    for violation in (3, 27, 55):
        print(f"{LspViolation(violation).explain:s}")
        print()

    print("--- d")
    print()

    for violation in (3, 27, 55):
        print(f"{LspViolation(violation).explain:d}")
        print()

    print("--- r")
    print()

    for violation in (3, 27, 55):
        print(f"{LspViolation(violation).explain:r}")
        print()

    print("--- o")
    print()

    for violation in (3, 27, 55):
        print(f"{LspViolation(violation).explain:o}")
        print()

    print("--- direct")
    print()

    for violation in (3, 27, 55):
        print(LspViolation(violation).explain)
        print()

    print(_COLORED_LSP_NAME)
    print(_COLORED_LSP_NAME.pattern)
    print(_COLORED_LSP_NAME.color_pattern)
