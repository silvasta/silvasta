"""
Explain the Rules of the LSP Violation Levels

-
"""

from typing import Any

__all__: list[str] = [
    "LspViolationDetail",
    "explain_lsp_violation",
]

from ...port.casting import LspViolation
from ...port.primitives import ExplainedTuple
from .. import reflect

type LspViolationDetail = ExplainedTuple[LspViolation]


def explain_lsp_violation() -> dict[LspViolation, ExplainedTuple[LspViolation]]:
    """Build the lazy-loaded explanation mapping for LspViolation."""
    return ExplainedTuple.table(
        ExplainedTuple(
            LspViolation.ZERO,
            "No violation",
            "Replacement signature is strictly LSP-compliant; not even positional-only parameter renaming is permitted.",
        ),
        #  LINE: -- Positional -- -- - -- -- - -- -- - -- -- - -- -- - -- --
        ExplainedTuple(
            LspViolation.POS_ONLY_RENAMED,
            "Positional-only parameter renamed",
            "Callers cannot pass positional-only parameters by keyword, so runtime calls never break, though strict reflection or stub checkers flag the name mismatch.",
        ),
        ExplainedTuple(
            LspViolation.DROPPED_VAR_POS,
            "Variadic positional absorption lost",
            "Baseline promised infinite positional argument absorption via *args; replacement caps positional arity.",
        ),
        ExplainedTuple(
            LspViolation.REDUCED_MAX_POS,
            "Finite positional capacity reduced",
            "Baseline accepted a larger finite number of positional arguments than replacement; fails when optional positional arguments are supplied.",
        ),
        ExplainedTuple(
            LspViolation.INCREASED_MIN_POS,
            "Minimum required positional arguments increased",
            "Replacement demands more positional arguments than baseline's minimum (by removing a default or adding a required parameter).",
        ),
        #  LINE: -- Keyword / Binding Vectors -- -- - -- -- - -- -- - -- --
        ExplainedTuple(
            LspViolation.DROPPED_VAR_KW,
            "Keyword absorption lost",
            "Baseline absorbed arbitrary keyword arguments; replacement rejects unknown keys with TypeError.",
        ),
        ExplainedTuple(
            LspViolation.LOST_KW_ACCESS,
            "Keyword access vector removed",
            "Parameter still exists at the same position, but changed from positional-or-keyword to positional-only (/); callers passing it by keyword fail with TypeError.",
        ),
        ExplainedTuple(
            LspViolation.LOST_POS_ACCESS,
            "Positional access vector removed",
            "Parameter still exists with the same name, but changed from positional-or-keyword to keyword-only (*); callers passing it positionally fail with TypeError.",
        ),
        ExplainedTuple(
            LspViolation.DROPPED_KW_NAME,
            "Named keyword parameter removed",
            "A specific keyword parameter accepted by baseline no longer exists and cannot be absorbed by **kwargs.",
        ),
        ExplainedTuple(
            LspViolation.ADDED_REQUIRED_KW,
            "Mandatory keyword parameter added",
            "Replacement introduces a new keyword-only parameter without a default value; standard callers fail with TypeError.",
        ),
        #  LINE: -- Parameter Types (Contravariance) -- -- - -- -- - -- --
        ExplainedTuple(
            LspViolation.ADDED_PARAM_CONSTRAINT,
            "Parameter type annotation added",
            "Baseline accepted Any (untyped), while replacement declares an explicit type constraint; safe in plain Python, fails under runtime type guards.",
        ),
        ExplainedTuple(
            LspViolation.NARROWED_PARAM_TYPE,
            "Parameter type narrowed (contravariance break)",
            "Replacement accepts a strict subtype of baseline's input; fails whenever a valid supertype or union branch from baseline is passed.",
        ),
        ExplainedTuple(
            LspViolation.DISJOINT_PARAM_TYPE,
            "Incompatible parameter type",
            "Replacement parameter type has zero overlap with baseline's parameter type; guaranteed failure for any valid baseline input.",
        ),
        #  LINE: -- Return Types (Covariance) -- -- - -- -- - -- -- - -- --
        ExplainedTuple(
            LspViolation.WIDENED_RETURN_SUPERSET,
            "Return type widened to superset (covariance break)",
            "Original return type remains included as a subtype or union member of the new return type; callers checking types dynamically can still handle it.",
        ),
        ExplainedTuple(
            LspViolation.OVERLAPPING_RETURN_UNION,
            "Return type partially shifted",
            "Intersection exists between baseline and replacement return types, but some baseline return types disappear while unexpected new types appear.",
        ),
        ExplainedTuple(
            LspViolation.DISJOINT_RETURN_TYPE,
            "Incompatible return type",
            "Replacement return type shares zero overlap with baseline's return type; safe only for sinks where the caller discards the return value.",
        ),
        #  LINE: -- Execution Semantics -- -- - -- -- - -- -- - -- -- - --
        ExplainedTuple(
            LspViolation.SYNC_ASYNC_MISMATCH,
            "Sync/async calling convention mismatch",
            "Switching between def and async def breaks the coroutine protocol: sync callers receive an unawaited coroutine, or async callers fail awaiting a non-awaitable.",
        ),
        ExplainedTuple(
            LspViolation.GENERATOR_MISMATCH,
            "Generator/eager execution mismatch",
            "Switching between a standard return and yield changes immediate execution into lazy iterator creation.",
        ),
        ExplainedTuple(
            LspViolation.DESCRIPTOR_BINDING_SHIFT,
            "Descriptor binding convention changed",
            "Changing between bound method, @classmethod, and @staticmethod alters implicit receiver (self/cls) injection and shifts positional indices.",
        ),
        #  LINE: -- Presets -- -- - -- -- - -- -- - -- -- - -- -- - -- --
        ExplainedTuple(
            LspViolation.HOOK_PLUGIN,
            "Plugin/hook extension preset",
            "Allows narrowing open *args/**kwargs extension points into concrete typed parameters while permitting positional-only renames.",
        ),
        ExplainedTuple(
            LspViolation.SINK_CALLBACK,
            "Fire-and-forget sink callback preset",
            "Ignores return type changes completely and allows dropping unused variadic or optional keyword arguments.",
        ),
        ExplainedTuple(
            LspViolation.MORPHING_INCLUSIVE,
            "Inclusive return-morphing preset",
            "Allows widening the return type as long as the baseline return type remains a valid subtype or member of the new return contract.",
        ),
        ExplainedTuple(
            LspViolation.MORPHING_ANY_RETURN,
            "Unrestricted return-morphing preset",
            "Allows replacing the return type with any type while preserving strict input call compatibility.",
        ),
    )


def check_param_variance(base_t: Any, new_t: Any) -> LspViolation:
    """Evaluate contravariant parameter type compatibility (base -> new)."""

    if reflect.types.is_untyped(new_t):
        return LspViolation.ZERO

    if reflect.types.is_untyped(base_t):
        return LspViolation.ADDED_PARAM_CONSTRAINT

    if reflect.types.is_subtype(base_t, new_t):
        return LspViolation.ZERO

    if reflect.types.overlap(base_t, new_t):
        return LspViolation.NARROWED_PARAM_TYPE

    return LspViolation.DISJOINT_PARAM_TYPE


def check_return_variance(base_r: Any, new_r: Any) -> LspViolation:
    """Evaluate covariant return type compatibility (base -> new)."""

    if reflect.types.is_untyped(base_r):
        return LspViolation.ZERO

    if reflect.types.is_untyped(new_r):
        return LspViolation.WIDENED_RETURN_SUPERSET

    if reflect.types.is_subtype(new_r, base_r):
        return LspViolation.ZERO

    if reflect.types.is_subtype(base_r, new_r):
        return LspViolation.WIDENED_RETURN_SUPERSET

    if reflect.types.overlap(base_r, new_r):
        return LspViolation.OVERLAPPING_RETURN_UNION

    return LspViolation.DISJOINT_RETURN_TYPE
