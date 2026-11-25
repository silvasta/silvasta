"""
Structural Capability Set Algebra for SigSpecing

 [-,&,|]

                      DependencyLevel.sstcore.brick.call.lsp[1.1:0]
"""

__all__: list[str] = [
    "subtract",
    "intersect",
    "union",
]

from dataclasses import replace
from inspect import _ParameterKind
from typing import Any

from ....port.empty import VOID
from ....port.sigspect import SigSpecing, SigVariable
from ... import reflect

type _SigVariables = tuple[SigVariable, ...]


def subtract[S: SigSpecing](left: S, right: S) -> S:
    """Compute structural capability difference (left - right)."""

    diff_pos: list[SigVariable] = [
        arg
        for index, arg in enumerate(left.pos)
        if index >= len(right.positionals)
    ]
    diff_both: list[SigVariable] = []
    diff_key: list[SigVariable] = []

    for offset, arg in enumerate(left.both):
        idx: int = len(left.pos) + offset
        has_pos: bool = idx < len(right.positionals)
        has_key: bool = arg.name in right.keyword_map

        if not has_pos and not has_key:
            diff_both.append(arg)
        elif not has_pos and has_key:
            diff_pos.append(arg.evolve(kind=_ParameterKind.POSITIONAL_ONLY))
        elif has_pos and not has_key:
            diff_key.append(arg.evolve(kind=_ParameterKind.KEYWORD_ONLY))

    for arg in left.key:
        if arg.name not in right.keyword_map:
            diff_key.append(arg)

    diff_args: _SigVariables = (
        left.args if (left.args and not right.args) else ()
    )
    diff_kwargs: _SigVariables = (
        left.kwargs if (left.kwargs and not right.kwargs) else ()
    )
    diff_result: Any = (
        VOID
        if reflect.types.is_subtype(right.result, left.result)
        else left.result
    )
    return replace(
        left,
        pos=tuple(diff_pos),
        both=tuple(diff_both),
        args=diff_args,
        key=tuple(diff_key),
        kwargs=diff_kwargs,
        result=diff_result,
    )


def intersect[S: SigSpecing](left: S, right: S) -> S:
    """Compute structural capability intersection (left & right)."""

    and_pos: list[SigVariable] = [
        arg for i, arg in enumerate(left.pos) if i < len(right.positionals)
    ]
    and_both: list[SigVariable] = []
    and_key: list[SigVariable] = []

    for offset, arg in enumerate(left.both):
        idx = len(left.pos) + offset
        has_pos = idx < len(right.positionals)
        has_key = arg.name in right.keyword_map

        if has_pos and has_key:
            and_both.append(arg)
        elif has_pos and not has_key:
            and_pos.append(arg.evolve(kind=_ParameterKind.POSITIONAL_ONLY))
        elif not has_pos and has_key:
            and_key.append(arg.evolve(kind=_ParameterKind.KEYWORD_ONLY))

    for arg in left.key:
        if arg.name in right.keyword_map:
            and_key.append(arg)

    and_args: _SigVariables = left.args if (left.args and right.args) else ()
    and_kwargs: _SigVariables = (
        left.kwargs if (left.kwargs and right.kwargs) else ()
    )
    if reflect.types.is_subtype(left.result, right.result):
        and_result: Any = left.result
    elif reflect.types.is_subtype(right.result, left.result):
        and_result: Any = right.result
    else:
        and_result: VOID = VOID

    return replace(
        left,
        pos=tuple(and_pos),
        both=tuple(and_both),
        args=and_args,
        key=tuple(and_key),
        kwargs=and_kwargs,
        result=and_result,
    )


def union[S: SigSpecing](left: S, right: S) -> S:
    """Compute structural capability union (left | right)."""
    remaining: SigSpecing = subtract(left=right, right=left)  # AI: proper?
    return replace(
        left,
        pos=left.pos + remaining.pos,
        both=left.both + remaining.both,
        args=left.args or right.args,
        key=left.key + remaining.key,
        kwargs=left.kwargs or right.kwargs,
        result=right.result if left.result is VOID else left.result,
    )


def _union[S: SigSpecing](left: S, right: S) -> S:
    # CHECK: Why left | right = left + (right - left) Breaks union
    # - maybe this will be reqired at some point
    """Compute structural capability union (left | right)."""
    left_pos = left.positionals
    right_pos = right.positionals
    left_kw = left.keyword_map
    right_kw = right.keyword_map

    # 1. Merge positional slots 0..max_len-1 without shifting indices
    slots: list[SigVariable] = []
    for i in range(max(len(left_pos), len(right_pos))):
        if i < len(left_pos):
            arg = left_pos[i]
            if (
                arg.kind is _ParameterKind.POSITIONAL_ONLY
                and arg.name in right_kw
            ):
                arg = arg.evolve(kind=_ParameterKind.POSITIONAL_OR_KEYWORD)
        else:
            arg = right_pos[i]
            if (
                arg.kind is _ParameterKind.POSITIONAL_ONLY
                and arg.name in left_kw
            ):
                arg = arg.evolve(kind=_ParameterKind.POSITIONAL_OR_KEYWORD)
        slots.append(arg)

    # 2. Split at the first POS_OR_KW (Python allows only one `/` boundary)
    slash_idx = next(
        (
            i
            for i, arg in enumerate(slots)
            if arg.kind is _ParameterKind.POSITIONAL_OR_KEYWORD
        ),
        len(slots),
    )
    uni_pos: list[SigVariable] = slots[:slash_idx]
    uni_both: list[SigVariable] = [
        arg
        if arg.kind is _ParameterKind.POSITIONAL_OR_KEYWORD
        else arg.evolve(kind=_ParameterKind.POSITIONAL_OR_KEYWORD)
        for arg in slots[slash_idx:]
    ]

    # 3. Collect remaining keyword-only parameters without duplicating names
    taken: set[str] = {arg.name for arg in (*uni_pos, *uni_both)}
    uni_key: list[SigVariable] = []
    for arg in (*left.key, *right_kw.values()):
        if arg.name in taken:
            continue
        taken.add(arg.name)
        uni_key.append(
            arg
            if arg.kind is _ParameterKind.KEYWORD_ONLY
            else arg.evolve(kind=_ParameterKind.KEYWORD_ONLY)
        )

    # 4. Join return types symmetrically (dual of intersect)
    uni_result: Any
    if left.result is VOID:
        uni_result = right.result
    elif right.result is VOID:
        uni_result = left.result
    elif reflect.types.is_subtype(left.result, right.result):
        uni_result = right.result
    elif reflect.types.is_subtype(right.result, left.result):
        uni_result = left.result
    else:
        uni_result = left.result

    return replace(
        left,
        pos=tuple(uni_pos),
        both=tuple(uni_both),
        args=left.args or right.args,
        key=tuple(uni_key),
        kwargs=left.kwargs or right.kwargs,
        result=uni_result,
    )
