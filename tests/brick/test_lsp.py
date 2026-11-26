"""Unit tests for sstcore.brick.call.lsp (SigVar, SigSpec, LspRules, Algebra, Explain)."""

from collections.abc import Callable
from inspect import Parameter, _ParameterKind
from typing import Any

import pytest

from sstcore.brick.call.lsp import (
    SigSpec,
    SigVar,
    allows,
    check_param_variance,
    check_return_variance,
    evaluate,
    explain_lsp_violation,
)
from sstcore.port.empty import VOID
from sstcore.port.sigspect import LspViolation

# ============================================================================
# 1. SigVar Tests
# ============================================================================


class TestSigVar:
    def test_normalization_and_properties(self) -> None:
        v_empty = SigVar(
            "x",
            _ParameterKind.POSITIONAL_OR_KEYWORD,
            Parameter.empty,
            Parameter.empty,
        )
        assert v_empty.name == "x"
        assert v_empty.default is VOID
        assert v_empty.annotation is VOID
        assert not v_empty.has_default
        assert not v_empty.has_annotation
        assert str(v_empty) == "SigVar[x]::POSITIONAL_OR_KEYWORD"

        v_full = SigVar(
            "y", _ParameterKind.KEYWORD_ONLY, default=42, annotation=int
        )
        assert v_full.has_default
        assert v_full.has_annotation
        assert v_full.default == 42
        assert v_full.annotation is int

    def test_evolve(self) -> None:
        v = SigVar(
            "a", _ParameterKind.POSITIONAL_OR_KEYWORD, default=1, annotation=int
        )
        v2 = v.evolve(name="b", kind=_ParameterKind.KEYWORD_ONLY, default=VOID)
        assert v2.name == "b"
        assert v2.kind is _ParameterKind.KEYWORD_ONLY
        assert not v2.has_default
        assert v2.annotation is int  # preserved


# ============================================================================
# 2. SigSpec Detection & Single-Spec Views
# ============================================================================


class TestSigSpecViews:
    def test_detect_buckets_and_views(self) -> None:
        def sample(
            a: int,
            b: str = "x",
            /,
            c: float = 1.0,
            *args: int,
            d: bool,
            e: int = 2,
            **kwargs: Any,
        ) -> str:
            return b

        spec = SigSpec.detect(sample)

        assert len(spec.pos) == 2
        assert len(spec.both) == 1
        assert len(spec.args) == 1
        assert len(spec.key) == 2
        assert len(spec.kwargs) == 1
        assert spec.result is str
        assert not spec.is_async
        assert not spec.is_generator

        assert [p.name for p in spec.positionals] == ["a", "b", "c"]
        assert set(spec.keyword_map) == {"c", "d", "e"}
        assert spec.both_indices == {"c": 2}
        assert spec.min_pos_only == 1
        assert spec.min_positional == 1
        assert spec.max_positional is None
        assert [p.name for p in spec.required] == ["a", "d"]
        assert spec.has_var_positional
        assert spec.has_var_keyword

    def test_finite_max_positional(self) -> None:
        def finite(a: int, b: int = 1, /, c: int = 2) -> None:
            pass

        spec = SigSpec.detect(finite)
        assert spec.min_positional == 1
        assert spec.max_positional == 3
        assert not spec.has_var_positional
        assert not spec.has_var_keyword

    def test_bind_self(self) -> None:
        def method_like(self, a: int, b: str = "ok") -> int:
            return a

        spec = SigSpec.detect(method_like)
        bound = spec.bind_self()
        assert [p.name for p in bound.both] == ["a", "b"]

        no_pos = SigSpec.detect(lambda *, k: k)
        with pytest.raises(TypeError, match="Cannot bind receiver"):
            no_pos.bind_self()


# ============================================================================
# 3. Atomic LSP Violation Predicates
# ============================================================================


def async_fn(x: int) -> int: ...  # helper defined inside test below


class _DummyClass:
    def inst_method(self, x: int) -> int:
        return x

    @classmethod
    def cls_method(cls, x: int) -> int:
        return x

    @staticmethod
    def static_method(x: int) -> int:
        return x


class TestLspAtomicRules:
    @pytest.mark.parametrize(
        ("base_fn", "new_fn", "expected_flag"),
        [
            # Positional rules
            (lambda a, /: a, lambda b, /: b, LspViolation.POS_ONLY_RENAMED),
            (
                lambda a, *args: a,
                lambda a, b=1: a,
                LspViolation.DROPPED_VAR_POS,
            ),
            (lambda a, b=1: a, lambda a: a, LspViolation.REDUCED_MAX_POS),
            (lambda a=1: a, lambda a: a, LspViolation.INCREASED_MIN_POS),
            (lambda a: a, lambda a, b: a, LspViolation.INCREASED_MIN_POS),
            # Keyword / binding vector rules
            (lambda a, **kw: a, lambda a: a, LspViolation.DROPPED_VAR_KW),
            (lambda a: a, lambda a, /: a, LspViolation.LOST_KW_ACCESS),
            (lambda a: a, lambda *, a=1: a, LspViolation.LOST_POS_ACCESS),
            (lambda *, a=1: a, lambda: None, LspViolation.DROPPED_KW_NAME),
            (lambda a: a, lambda a, *, req: a, LspViolation.ADDED_REQUIRED_KW),
            (
                lambda a, /, *, b=1: a,
                lambda a, b=1: a,
                LspViolation.POS_KW_COLLISION,
            ),
        ],
    )
    def test_structural_violations(
        self,
        base_fn: Callable[..., Any],
        new_fn: Callable[..., Any],
        expected_flag: LspViolation,
    ) -> None:
        base = SigSpec.detect(base_fn)
        new = SigSpec.detect(new_fn)
        violations = evaluate(base, new)
        assert expected_flag in violations
        assert not allows(base, new)
        assert allows(base, new, tolerance=violations)

    def test_execution_semantics_violations(self) -> None:
        def sync_fn(x: int) -> int:
            return x

        async def async_fn(x: int) -> int:
            return x

        def gen_fn(x: int):
            yield x

        s_sync = SigSpec.detect(sync_fn)
        s_async = SigSpec.detect(async_fn)
        s_gen = SigSpec.detect(gen_fn)

        assert LspViolation.SYNC_ASYNC_MISMATCH in s_sync.diff(s_async)
        assert LspViolation.GENERATOR_MISMATCH in s_sync.diff(s_gen)

        inst_obj = _DummyClass()
        s_bound = SigSpec.detect(inst_obj.inst_method)
        s_static = SigSpec.detect(_DummyClass.static_method)
        assert LspViolation.DESCRIPTOR_BINDING_SHIFT in s_bound.diff(s_static)


# ============================================================================
# 4. Parameter Contravariance & Return Covariance
# ============================================================================


class Animal:
    pass


class Dog(Animal):
    pass


class Bulldog(Dog):
    pass


class TestTypeVariance:
    def test_param_contravariance(self) -> None:
        # Contravariant: widening param (Dog -> Animal or Any) is valid (ZERO)
        assert check_param_variance(Dog, Animal) is LspViolation.ZERO
        assert check_param_variance(Dog, Dog) is LspViolation.ZERO
        assert check_param_variance(Dog, VOID) is LspViolation.ZERO

        # Adding constraint to untyped param
        assert (
            check_param_variance(VOID, Dog)
            is LspViolation.ADDED_PARAM_CONSTRAINT
        )

        # Narrowing param (Animal -> Dog, or int | str -> int)
        assert (
            check_param_variance(Animal, Dog)
            is LspViolation.NARROWED_PARAM_TYPE
        )
        assert (
            check_param_variance(int | str, int)
            is LspViolation.NARROWED_PARAM_TYPE
        )

        # Disjoint param (int -> str)
        assert (
            check_param_variance(int, str) is LspViolation.DISJOINT_PARAM_TYPE
        )

    def test_return_covariance(self) -> None:
        # Covariant: narrowing return (Animal -> Dog) is valid (ZERO)
        assert check_return_variance(Animal, Dog) is LspViolation.ZERO
        assert check_return_variance(Dog, Dog) is LspViolation.ZERO
        assert check_return_variance(VOID, Dog) is LspViolation.ZERO

        # Widening return to superset or untyped (Dog -> Animal, Dog -> VOID)
        assert (
            check_return_variance(Dog, Animal)
            is LspViolation.WIDENED_RETURN_SUPERSET
        )
        assert (
            check_return_variance(Dog, VOID)
            is LspViolation.WIDENED_RETURN_SUPERSET
        )

        # Overlapping union shift (int | str -> int | bytes)
        assert (
            check_return_variance(int | str, int | bytes)
            is LspViolation.OVERLAPPING_RETURN_UNION
        )

        # Disjoint return (int -> str)
        assert (
            check_return_variance(int, str) is LspViolation.DISJOINT_RETURN_TYPE
        )

    def test_end_to_end_signature_variance(self) -> None:
        def base(pet: Dog) -> Animal:
            return pet

        def valid_sub(pet: Animal) -> Bulldog:
            return Bulldog()

        def invalid_sub(pet: Bulldog) -> object:
            return object()

        s_base = SigSpec.detect(base)
        s_valid = SigSpec.detect(valid_sub)
        s_invalid = SigSpec.detect(invalid_sub)

        assert s_base.diff(s_valid) is LspViolation.ZERO
        assert s_base.allows(s_valid)

        diff = s_base.diff(s_invalid)
        assert LspViolation.NARROWED_PARAM_TYPE in diff
        assert LspViolation.WIDENED_RETURN_SUPERSET in diff


# ============================================================================
# 5. Presets & Operators
# ============================================================================


class TestOperatorsAndPresets:
    def test_comparison_and_shift_operators(self) -> None:
        def strict_fn(a: int) -> int:
            return a

        def flexible_fn(a: int | str, b: int = 0) -> int:
            return 1

        s_base = SigSpec.detect(strict_fn)
        s_sub = SigSpec.detect(flexible_fn)

        # s_sub can replace s_base, not vice-versa
        assert s_base >= s_sub
        assert s_base > s_sub
        assert s_sub <= s_base
        assert s_sub < s_base
        assert s_sub in s_base
        assert flexible_fn in s_base

        # Shift operators
        assert (s_base >> s_sub) is LspViolation.ZERO
        assert (s_sub << s_base) is LspViolation.ZERO
        assert LspViolation.REDUCED_MAX_POS in (s_sub >> s_base)
        assert LspViolation.REDUCED_MAX_POS in (s_base << s_sub)

    def test_hook_plugin_preset(self) -> None:
        def hook_spec(event, /, *args, **kwargs) -> bool:
            return True

        def concrete_plugin(evt: str, /, count: int = 1) -> bool:
            return count > 0

        base = SigSpec.detect(hook_spec, tolerance=LspViolation.HOOK_PLUGIN)
        assert not base.allows(
            SigSpec.detect(concrete_plugin), tolerance=LspViolation.ZERO
        )
        assert concrete_plugin in base

    def test_sink_callback_preset(self) -> None:
        def event_emitter(
            user_id: int, payload: dict, *, timestamp: float = 0.0
        ) -> int:
            return 200

        def minimal_sink(user_id: int) -> None:
            pass

        base = SigSpec.detect(
            event_emitter, tolerance=LspViolation.SINK_CALLBACK
        )
        assert minimal_sink in base


# ============================================================================
# 6. Capability Set Algebra (-, &, |)
# ============================================================================


class TestSigSpecAlgebra:
    def test_subtract_intersect_union(self) -> None:
        def fn_left(
            a: int, b: str = "x", *, k1: bool = True, k2: int = 0
        ) -> Animal:
            return Animal()

        def fn_right(
            a: int, *, b: str = "x", k2: int = 0, k3: float = 1.0
        ) -> Dog:
            return Dog()

        left = SigSpec.detect(fn_left)
        right = SigSpec.detect(fn_right)

        # Intersection:
        # - 'a' is both in left and right -> stays in `both`
        # - 'b' is pos+kw in left, but kw-only in right -> becomes `key` (KEYWORD_ONLY)
        # - 'k2' is in both -> stays in `key`
        # - return: Dog is subtype of Animal -> Dog
        inter = left & right
        assert [p.name for p in inter.both] == ["a"]
        assert {p.name for p in inter.key} == {"b", "k2"}
        assert inter.result is Dog

        # Difference (left - right):
        # - 'a' removed
        # - 'b' loses keyword capability (right has kw 'b'), retains POSITIONAL_ONLY
        # - 'k1' stays in key
        diff = left - right
        assert [p.name for p in diff.pos] == ["b"]
        assert [p.name for p in diff.both] == []
        assert [p.name for p in diff.key] == ["k1"]

        # Union (left | right):
        combined = left | right
        assert {p.name for p in combined.all_params} >= {
            "a",
            "b",
            "k1",
            "k2",
            "k3",
        }


# ============================================================================
# 7. Formatting & Explanations
# ============================================================================


class TestExplainAndFormatting:
    def test_all_flags_explained(self) -> None:
        table = explain_lsp_violation()
        for member in LspViolation:
            assert member in table
            explained = table[member]
            assert explained.title
            assert explained.detail

    def test_format_mini_language(self) -> None:
        flag = LspViolation.NARROWED_PARAM_TYPE
        assert f"{flag:b}" == flag.bits
        assert "Parameter type narrowed" in f"{flag:t}"
        assert "strict subtype" in f"{flag:e}"
        assert "—" in f"{flag:v}"
        assert "\n  " in f"{flag:vn}"
        assert f"{flag:i}".startswith("[ⓘ | ")
        assert " => " in f"{flag:v; => }"

    def test_combined_flag_explanation(self) -> None:
        combo = (
            LspViolation.INCREASED_MIN_POS | LspViolation.DISJOINT_RETURN_TYPE
        )
        rendered_multiline = f"{combo:vn}"
        assert f"[{LspViolation.INCREASED_MIN_POS.value}]" in rendered_multiline
        assert (
            f"[{LspViolation.DISJOINT_RETURN_TYPE.value}]" in rendered_multiline
        )
