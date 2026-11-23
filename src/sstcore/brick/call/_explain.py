"""
Explain the Rules of the LSP Violation Levels

-
"""

__all__: list[str] = [
    "LspViolationDetail",
    "explain_lsp_violation",
]

from ...port.casting import LspViolation
from ...port.primitives import ExplainTuple

type LspViolationDetail = ExplainTuple[LspViolation]


def explain_lsp_violation() -> dict[LspViolation, ExplainTuple[LspViolation]]:
    """Build the lazy-loaded explanation mapping for LspViolation."""
    return ExplainTuple.table(
        ExplainTuple(
            LspViolation.ZERO,
            "No violation",
            "Replacement signature is strictly LSP-compliant; not even positional-only parameter renaming is permitted.",
        ),
        #  LINE: -- Positional -- -- - -- -- - -- -- - -- -- - -- -- - -- --
        ExplainTuple(
            LspViolation.POS_ONLY_RENAMED,
            "Positional-only parameter renamed",
            "Callers cannot pass positional-only parameters by keyword, so runtime calls never break, though strict reflection or stub checkers flag the name mismatch.",
        ),
        ExplainTuple(
            LspViolation.DROPPED_VAR_POS,
            "Variadic positional absorption lost",
            "Baseline promised infinite positional argument absorption via *args; replacement caps positional arity.",
        ),
        ExplainTuple(
            LspViolation.REDUCED_MAX_POS,
            "Finite positional capacity reduced",
            "Baseline accepted a larger finite number of positional arguments than replacement; fails when optional positional arguments are supplied.",
        ),
        ExplainTuple(
            LspViolation.INCREASED_MIN_POS,
            "Minimum required positional arguments increased",
            "Replacement demands more positional arguments than baseline's minimum (by removing a default or adding a required parameter).",
        ),
        #  LINE: -- Keyword / Binding Vectors -- -- - -- -- - -- -- - -- --
        ExplainTuple(
            LspViolation.DROPPED_VAR_KW,
            "Keyword absorption lost",
            "Baseline absorbed arbitrary keyword arguments; replacement rejects unknown keys with TypeError.",
        ),
        ExplainTuple(
            LspViolation.LOST_KW_ACCESS,
            "Keyword access vector removed",
            "Parameter still exists at the same position, but changed from positional-or-keyword to positional-only (/); callers passing it by keyword fail with TypeError.",
        ),
        ExplainTuple(
            LspViolation.LOST_POS_ACCESS,
            "Positional access vector removed",
            "Parameter still exists with the same name, but changed from positional-or-keyword to keyword-only (*); callers passing it positionally fail with TypeError.",
        ),
        ExplainTuple(
            LspViolation.DROPPED_KW_NAME,
            "Named keyword parameter removed",
            "A specific keyword parameter accepted by baseline no longer exists and cannot be absorbed by **kwargs.",
        ),
        ExplainTuple(
            LspViolation.ADDED_REQUIRED_KW,
            "Mandatory keyword parameter added",
            "Replacement introduces a new keyword-only parameter without a default value; standard callers fail with TypeError.",
        ),
        #  LINE: -- Parameter Types (Contravariance) -- -- - -- -- - -- --
        ExplainTuple(
            LspViolation.ADDED_PARAM_CONSTRAINT,
            "Parameter type annotation added",
            "Baseline accepted Any (untyped), while replacement declares an explicit type constraint; safe in plain Python, fails under runtime type guards.",
        ),
        ExplainTuple(
            LspViolation.NARROWED_PARAM_TYPE,
            "Parameter type narrowed (contravariance break)",
            "Replacement accepts a strict subtype of baseline's input; fails whenever a valid supertype or union branch from baseline is passed.",
        ),
        ExplainTuple(
            LspViolation.DISJOINT_PARAM_TYPE,
            "Incompatible parameter type",
            "Replacement parameter type has zero overlap with baseline's parameter type; guaranteed failure for any valid baseline input.",
        ),
        #  LINE: -- Return Types (Covariance) -- -- - -- -- - -- -- - -- --
        ExplainTuple(
            LspViolation.WIDENED_RETURN_SUPERSET,
            "Return type widened to superset (covariance break)",
            "Original return type remains included as a subtype or union member of the new return type; callers checking types dynamically can still handle it.",
        ),
        ExplainTuple(
            LspViolation.OVERLAPPING_RETURN_UNION,
            "Return type partially shifted",
            "Intersection exists between baseline and replacement return types, but some baseline return types disappear while unexpected new types appear.",
        ),
        ExplainTuple(
            LspViolation.DISJOINT_RETURN_TYPE,
            "Incompatible return type",
            "Replacement return type shares zero overlap with baseline's return type; safe only for sinks where the caller discards the return value.",
        ),
        #  LINE: -- Execution Semantics -- -- - -- -- - -- -- - -- -- - --
        ExplainTuple(
            LspViolation.SYNC_ASYNC_MISMATCH,
            "Sync/async calling convention mismatch",
            "Switching between def and async def breaks the coroutine protocol: sync callers receive an unawaited coroutine, or async callers fail awaiting a non-awaitable.",
        ),
        ExplainTuple(
            LspViolation.GENERATOR_MISMATCH,
            "Generator/eager execution mismatch",
            "Switching between a standard return and yield changes immediate execution into lazy iterator creation.",
        ),
        ExplainTuple(
            LspViolation.DESCRIPTOR_BINDING_SHIFT,
            "Descriptor binding convention changed",
            "Changing between bound method, @classmethod, and @staticmethod alters implicit receiver (self/cls) injection and shifts positional indices.",
        ),
        #  LINE: -- Presets -- -- - -- -- - -- -- - -- -- - -- -- - -- --
        ExplainTuple(
            LspViolation.HOOK_PLUGIN,
            "Plugin/hook extension preset",
            "Allows narrowing open *args/**kwargs extension points into concrete typed parameters while permitting positional-only renames.",
        ),
        ExplainTuple(
            LspViolation.SINK_CALLBACK,
            "Fire-and-forget sink callback preset",
            "Ignores return type changes completely and allows dropping unused variadic or optional keyword arguments.",
        ),
        ExplainTuple(
            LspViolation.MORPHING_INCLUSIVE,
            "Inclusive return-morphing preset",
            "Allows widening the return type as long as the baseline return type remains a valid subtype or member of the new return contract.",
        ),
        ExplainTuple(
            LspViolation.MORPHING_ANY_RETURN,
            "Unrestricted return-morphing preset",
            "Allows replacing the return type with any type while preserving strict input call compatibility.",
        ),
    )
