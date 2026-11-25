"""
LSP Signature Rules and Variance Evaluators

- Atomic (base, new) predicates operating on the SigSpecing protocol
- Contravariant parameter and covariant return variance evaluators
- LspRules: frozen declarative SSoT registry of all LSP checks

                      DependencyLevel.sstcore.brick.call.lsp[1.1:0]
"""

__all__: list[str] = [
    "LspRules",
    "evaluate",
    "allows",
    "check_param_variance",
    "check_return_variance",
]

from collections.abc import Callable, Iterator, Mapping
from inspect import _ParameterKind
from typing import Any

from ....port._presets import PresetMeta
from ....port.empty import MayNot
from ....port.sigspect import LspViolation, SigSpecing
from ... import reflect

#  LINE: -- Atomic Predicates: Execution Semantics -- -- - -- -- - -- --


def _sync_async_mismatch(base: SigSpecing, new: SigSpecing) -> bool:
    return base.is_async != new.is_async


def _generator_mismatch(base: SigSpecing, new: SigSpecing) -> bool:
    return base.is_generator != new.is_generator


def _descriptor_binding_shift(base: SigSpecing, new: SigSpecing) -> bool:
    return base.binding != new.binding


#  LINE: -- Atomic Predicates: Positional -- -- - -- -- - -- -- - -- --


def _pos_only_renamed(base: SigSpecing, new: SigSpecing) -> bool:
    return any(
        b.name != n.name
        for b, n in zip(base.pos, new.positionals, strict=False)
    )


def _dropped_var_pos(base: SigSpecing, new: SigSpecing) -> bool:
    return bool(base.args and not new.args)


def _reduced_max_pos(base: SigSpecing, new: SigSpecing) -> bool:
    return not new.args and len(new.positionals) < len(base.positionals)


def _increased_min_pos(base: SigSpecing, new: SigSpecing) -> bool:
    for i, arg in enumerate(new.positionals):
        if arg.has_default:
            continue
        if i < len(base.positionals):
            if base.positionals[i].has_default:
                return True
            if (
                arg.kind is _ParameterKind.POSITIONAL_ONLY
                and i >= base.min_pos_only
                and arg.name != base.positionals[i].name
            ):
                return True
        else:
            promoted_required_kw = (
                not base.args
                and arg.kind is _ParameterKind.POSITIONAL_OR_KEYWORD
                and arg.name in base.keyword_map
                and not base.keyword_map[arg.name].has_default
            )
            if not promoted_required_kw:
                return True
    return False


#  LINE: -- Atomic Predicates: Keyword / Binding Vectors -- -- - -- --


def _dropped_var_kw(base: SigSpecing, new: SigSpecing) -> bool:
    return bool(base.kwargs and not new.kwargs)


def _lost_kw_access(base: SigSpecing, new: SigSpecing) -> bool:
    for name, idx in base.both_indices.items():
        if name in new.keyword_map:
            continue
        if idx < len(new.pos) and new.pos[idx].name == name:
            if not new.kwargs or not new.pos[idx].has_default:
                return True
    return False


def _lost_pos_access(base: SigSpecing, new: SigSpecing) -> bool:
    """Catch both->key demotion and POS_OR_KW positional index shifts"""

    for name, idx in base.both_indices.items():
        if name not in new.keyword_map:
            continue
        if name not in new.both_indices or new.both_indices[name] != idx:
            return True
    return False


def _dropped_kw_name(base: SigSpecing, new: SigSpecing) -> bool:
    if new.kwargs:
        return False

    for name in base.keyword_map:
        if name in new.keyword_map:
            continue
        idx: MayNot[int] = base.both_indices.get(name)
        if idx is not None and idx < len(new.pos) and new.pos[idx].name == name:
            continue
        return True
    return False


def _added_required_kw(base: SigSpecing, new: SigSpecing) -> bool:

    for arg in new.key:
        if not arg.has_default and (
            arg.name not in base.keyword_map
            or base.keyword_map[arg.name].has_default
        ):
            return True

    for offset, arg in enumerate(new.both):
        if arg.has_default:
            continue
        idx: int = len(new.pos) + offset
        if arg.name not in base.keyword_map:
            if idx >= base.min_pos_only:
                return True
        elif base.keyword_map[
            arg.name
        ].has_default and idx != base.both_indices.get(arg.name):
            return True

    return False


def _pos_kw_collision(base: SigSpecing, new: SigSpecing) -> bool:
    """Detect POS_OR_KW params where a valid base call sends both pos & kw."""

    for name, idx in new.both_indices.items():
        if not (base.args or idx < len(base.positionals)):
            continue
        if not (base.kwargs or name in base.keyword_map):
            continue
        base_idx: MayNot[int] = base.both_indices.get(name)
        if base_idx is None or base_idx > idx:
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


def _iter_param_type_pairs(
    base: SigSpecing, new: SigSpecing
) -> Iterator[tuple[Any, Any]]:
    """Yield every (base_type, new_type) binding pair across pos/kw/varargs."""

    overlap: int = min(len(base.positionals), len(new.positionals))

    # 1. Direct positional overlap
    for i in range(overlap):
        yield base.positionals[i].annotation, new.positionals[i].annotation

    # 2. New *args absorbs trailing base positionals and base *args
    if new.args:
        new_var_t = new.args[0].annotation
        for i in range(overlap, len(base.positionals)):
            yield base.positionals[i].annotation, new_var_t
        if base.args:
            yield base.args[0].annotation, new_var_t

    # 3. Base *args feeds extra concrete positional params in new
    if base.args:
        base_var_t = base.args[0].annotation
        for i in range(len(base.positionals), len(new.positionals)):
            yield base_var_t, new.positionals[i].annotation

    # 4. Named keyword matches and new **kwargs absorption
    for name, base_arg in base.keyword_map.items():
        if name in new.keyword_map:
            if (
                name in base.both_indices
                and new.both_indices.get(name) == base.both_indices[name]
            ):
                continue  # Already checked in step 1
            yield base_arg.annotation, new.keyword_map[name].annotation
        elif new.kwargs:
            yield base_arg.annotation, new.kwargs[0].annotation

    # 5. Base **kwargs feeds new **kwargs and newly introduced keyword params
    if base.kwargs:
        base_kw_t = base.kwargs[0].annotation
        if new.kwargs:
            yield base_kw_t, new.kwargs[0].annotation
        for name, new_arg in new.keyword_map.items():
            if name not in base.keyword_map:
                yield base_kw_t, new_arg.annotation


def _eval_param_variance(base: SigSpecing, new: SigSpecing) -> LspViolation:
    found: LspViolation = LspViolation.ZERO
    for base_t, new_t in _iter_param_type_pairs(base, new):
        found |= check_param_variance(base_t, new_t)
    return found


def _eval_return_variance(base: SigSpecing, new: SigSpecing) -> LspViolation:
    return check_return_variance(base.result, new.result)


#  LINE: -- Rule Registry & Evaluation Entrypoints -- -- - -- -- - -- --


class LspRules(metaclass=PresetMeta):
    """Declarative SSoT registry of all atomic LSP rules"""

    type Predicate = Callable[[SigSpecing, SigSpecing], bool]
    type Evaluator = Callable[[SigSpecing, SigSpecing], LspViolation]

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

    PREDICATES: Mapping[LspViolation, Predicate] = {
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
        LspViolation.POS_KW_COLLISION: _pos_kw_collision,
    }

    EVALUATORS: Mapping[LspViolation, Evaluator] = {
        _PARAM_MASK: _eval_param_variance,
        _RETURN_MASK: _eval_return_variance,
    }


def evaluate(
    base: SigSpecing,
    new: SigSpecing,
    *,
    ignore: LspViolation = LspViolation.ZERO,
) -> LspViolation:
    """Compute all active LSP violations when substituting Base with New"""

    found: LspViolation = LspViolation.ZERO

    for flag, predicate in LspRules.PREDICATES.items():
        if (flag & ~ignore) and predicate(base, new):
            found |= flag

    for mask, evaluator in LspRules.EVALUATORS.items():
        if mask & ~ignore:
            found |= evaluator(base, new) & ~ignore

    return found


def allows(
    base: SigSpecing,
    new: SigSpecing,
    tolerance: LspViolation = LspViolation.ZERO,
) -> bool:
    """Check if New may Substitute Base under Tolerance"""

    for flag, predicate in LspRules.PREDICATES.items():
        if (flag & ~tolerance) and predicate(base, new):
            return False

    for mask, evaluator in LspRules.EVALUATORS.items():
        if (mask & ~tolerance) and (evaluator(base, new) & ~tolerance):
            return False

    return True
