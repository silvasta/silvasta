"""
LSP Signature Rules, Variance Evaluators, and Violation Explanations

- SigVariable / SigSpecing: structural protocols decoupling rules from SigSpec
- _SigPair: pre-indexed comparison context allocated once per evaluation
- PREDICATES / EVALUATORS: declarative SSoT registry of all atomic LSP rules

"""

__all__: list[str] = [
    "LspRules",
    "evaluate",
    "allows",
    "check_param_variance",
    "check_return_variance",
]

from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from inspect import _ParameterKind
from typing import Any, NamedTuple, Self

from ...port._presets import PresetMeta
from ...port.casting import LspViolation, SigSpecing, SigVariable
from .. import reflect

type _Predicate = Callable[[SigSpecing, SigSpecing], bool]
type _Evaluator = Callable[[SigSpecing, SigSpecing], LspViolation]


@dataclass(frozen=True, slots=True)
class _SigPair:
    # AI_TASK: resolve this, why not just a tuple that holds 2 classes?
    """Normalized comparison views computed once per diff/allows call."""

    base: SigSpecing
    new: SigSpecing
    base_pos: tuple[SigVariable, ...]
    new_pos: tuple[SigVariable, ...]
    base_kw: dict[str, SigVariable]
    new_kw: dict[str, SigVariable]
    base_both_idx: dict[str, int]
    new_both_idx: dict[str, int]
    base_min_pos_only: int

    @classmethod
    def build(cls, base: SigSpecing, new: SigSpecing) -> Self:
        base_pos = (*base.pos, *base.both)
        new_pos = (*new.pos, *new.both)
        return cls(
            base=base,
            new=new,
            base_pos=base_pos,
            new_pos=new_pos,
            base_kw={arg.name: arg for arg in (*base.both, *base.key)},
            new_kw={arg.name: arg for arg in (*new.both, *new.key)},
            base_both_idx={
                arg.name: len(base.pos) + i for i, arg in enumerate(base.both)
            },
            new_both_idx={
                arg.name: len(new.pos) + i for i, arg in enumerate(new.both)
            },
            base_min_pos_only=sum(1 for a in base.pos if not a.has_default),
        )


def _dropped_var_pos(base: SigSpecing, new: SigSpecing) -> bool:
    return bool(base.args and not new.args)


class SigSpecPair(NamedTuple):  # AI: this looks already like it is enough
    left: SigSpecing
    right: SigSpecing


#  LINE: -- Atomic Predicates: Execution Semantics -- -- - -- -- - -- --


def _sync_async_mismatch(p: _SigPair) -> bool:
    return p.base.is_async != p.new.is_async


def _generator_mismatch(p: _SigPair) -> bool:
    return p.base.is_generator != p.new.is_generator


def _descriptor_binding_shift(p: _SigPair) -> bool:
    return p.base.binding != p.new.binding


#  LINE: -- Atomic Predicates: Positional -- -- - -- -- - -- -- - -- --


def _pos_only_renamed(p: _SigPair) -> bool:
    return any(
        b.name != n.name for b, n in zip(p.base.pos, p.new_pos, strict=False)
    )


def _dropped_var_pos(p: _SigPair) -> bool:
    return bool(p.base.args and not p.new.args)


def _reduced_max_pos(p: _SigPair) -> bool:
    return not p.new.args and len(p.new_pos) < len(p.base_pos)


def _increased_min_pos(p: _SigPair) -> bool:
    base_len = len(p.base_pos)
    for i, arg in enumerate(p.new_pos):
        if arg.has_default:
            continue
        if i < base_len:
            if p.base_pos[i].has_default:
                return True
            if (
                arg.kind is _ParameterKind.POSITIONAL_ONLY
                and i >= p.base_min_pos_only
                and arg.name != p.base_pos[i].name
            ):
                return True
        else:
            promoted_required_kw = (
                not p.base.args
                and arg.kind is _ParameterKind.POSITIONAL_OR_KEYWORD
                and arg.name in p.base_kw
                and not p.base_kw[arg.name].has_default
            )
            if not promoted_required_kw:
                return True
    return False


#  LINE: -- Atomic Predicates: Keyword / Binding Vectors -- -- - -- --


def _dropped_var_kw(p: _SigPair) -> bool:
    return bool(p.base.kwargs and not p.new.kwargs)


def _lost_kw_access(p: _SigPair) -> bool:
    new_pos_only_len = len(p.new.pos)
    for name, idx in p.base_both_idx.items():
        if name in p.new_kw:
            continue
        if idx < new_pos_only_len and p.new.pos[idx].name == name:
            if not p.new.kwargs or not p.new.pos[idx].has_default:
                return True
    return False


def _lost_pos_access(p: _SigPair) -> bool:
    """Catch both->key demotion and POS_OR_KW positional index shifts."""
    for name, idx in p.base_both_idx.items():
        if name not in p.new_kw:
            continue
        if name not in p.new_both_idx or p.new_both_idx[name] != idx:
            return True
    return False


def _dropped_kw_name(p: _SigPair) -> bool:
    if p.new.kwargs:
        return False
    new_pos_only_len = len(p.new.pos)
    for name in p.base_kw:
        if name in p.new_kw:
            continue
        idx = p.base_both_idx.get(name)
        if (
            idx is not None
            and idx < new_pos_only_len
            and p.new.pos[idx].name == name
        ):
            continue
        return True
    return False


def _added_required_kw(p: _SigPair) -> bool:
    for arg in p.new.key:
        if not arg.has_default and (
            arg.name not in p.base_kw or p.base_kw[arg.name].has_default
        ):
            return True

    new_pos_only_len = len(p.new.pos)
    for offset, arg in enumerate(p.new.both):
        if arg.has_default:
            continue
        idx = new_pos_only_len + offset
        if arg.name not in p.base_kw:
            if idx >= p.base_min_pos_only:
                return True
        elif p.base_kw[arg.name].has_default and idx != p.base_both_idx.get(
            arg.name
        ):
            return True

    return False


#  LINE: -- Variance Evaluators -- -- - -- -- - -- -- - -- -- - -- --


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


#  LINE: --  -- - -- -- - -- -- - -- --


def _iter_param_type_pairs(p: _SigPair) -> Iterator[tuple[Any, Any]]:
    """Yield every (base_type, new_type) binding pair across pos/kw/varargs."""
    overlap = min(len(p.base_pos), len(p.new_pos))

    # 1. Direct positional overlap
    for i in range(overlap):
        yield p.base_pos[i].annotation, p.new_pos[i].annotation

    # 2. New *args absorbs trailing base positionals and base *args
    if p.new.args:
        new_var_t = p.new.args[0].annotation
        for i in range(overlap, len(p.base_pos)):
            yield p.base_pos[i].annotation, new_var_t
        if p.base.args:
            yield p.base.args[0].annotation, new_var_t

    # 3. Base *args feeds extra concrete positional params in new
    if p.base.args:
        base_var_t = p.base.args[0].annotation
        for i in range(len(p.base_pos), len(p.new_pos)):
            yield base_var_t, p.new_pos[i].annotation

    # 4. Named keyword matches and new **kwargs absorption
    for name, base_arg in p.base_kw.items():
        if name in p.new_kw:
            if (
                name in p.base_both_idx
                and p.new_both_idx.get(name) == p.base_both_idx[name]
            ):
                continue  # Already checked in step 1
            yield base_arg.annotation, p.new_kw[name].annotation
        elif p.new.kwargs:
            yield base_arg.annotation, p.new.kwargs[0].annotation

    # 5. Base **kwargs feeds new **kwargs and newly introduced keyword params
    if p.base.kwargs:
        base_kw_t = p.base.kwargs[0].annotation
        if p.new.kwargs:
            yield base_kw_t, p.new.kwargs[0].annotation
        for name, new_arg in p.new_kw.items():
            if name not in p.base_kw:
                yield base_kw_t, new_arg.annotation


def _eval_param_variance(p: _SigPair) -> LspViolation:
    found = LspViolation.ZERO
    for base_t, new_t in _iter_param_type_pairs(p):
        found |= check_param_variance(base_t, new_t)
    return found


def _eval_return_variance(p: _SigPair) -> LspViolation:
    return check_return_variance(p.base.result, p.new.result)


#  LINE: -- Rule Registry & Evaluation Entrypoints -- -- - -- -- - -- --


class LspRules(metaclass=PresetMeta):
    """Combine all Rules"""

    _PARAM_MASK = (
        LspViolation.ADDED_PARAM_CONSTRAINT
        | LspViolation.NARROWED_PARAM_TYPE
        | LspViolation.DISJOINT_PARAM_TYPE
    )
    _RETURN_MASK = (
        LspViolation.WIDENED_RETURN_SUPERSET
        | LspViolation.OVERLAPPING_RETURN_UNION
        | LspViolation.DISJOINT_RETURN_TYPE
    )

    PREDICATES: Mapping[LspViolation, _Predicate] = {
        # Execution Semantics
        LspViolation.SYNC_ASYNC_MISMATCH: _sync_async_mismatch,
        LspViolation.GENERATOR_MISMATCH: _generator_mismatch,
        LspViolation.DESCRIPTOR_BINDING_SHIFT: _descriptor_binding_shift,
        # Positional
        LspViolation.POS_ONLY_RENAMED: _pos_only_renamed,
        LspViolation.DROPPED_VAR_POS: _dropped_var_pos,
        LspViolation.REDUCED_MAX_POS: _reduced_max_pos,
        LspViolation.INCREASED_MIN_POS: _increased_min_pos,
        # Keyword / Binding Vectors
        LspViolation.DROPPED_VAR_KW: _dropped_var_kw,
        LspViolation.LOST_KW_ACCESS: _lost_kw_access,
        LspViolation.LOST_POS_ACCESS: _lost_pos_access,
        LspViolation.DROPPED_KW_NAME: _dropped_kw_name,
        LspViolation.ADDED_REQUIRED_KW: _added_required_kw,
    }

    EVALUATORS: Mapping[LspViolation, _Evaluator] = {
        _PARAM_MASK: _eval_param_variance,
        _RETURN_MASK: _eval_return_variance,
    }


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def evaluate(
    base: SigSpecing,
    new: SigSpecing,
    *,
    ignore: LspViolation = LspViolation.ZERO,
) -> LspViolation:
    pair: _SigPair = _SigPair.build(base, new)
    found: LspViolation = LspViolation.ZERO

    for flag, predicate in LspRules.PREDICATES.items():
        if (flag & ~ignore) and predicate(pair):
            found |= flag

    for mask, evaluator in LspRules.EVALUATORS.items():
        if mask & ~ignore:
            found |= evaluator(pair) & ~ignore

    return found


def allows(
    base: SigSpecing,
    new: SigSpecing,
    tolerance: LspViolation = LspViolation.ZERO,
) -> bool:
    """Check whether `new` may substitute `base` under `tolerance` (fast-fail)."""
    pair: _SigPair = _SigPair.build(base, new)

    for flag, predicate in LspRules.PREDICATES.items():
        if (flag & ~tolerance) and predicate(pair):
            return False

    for mask, evaluator in LspRules.EVALUATORS.items():
        if (mask & ~tolerance) and (evaluator(pair) & ~tolerance):
            return False

    return True
