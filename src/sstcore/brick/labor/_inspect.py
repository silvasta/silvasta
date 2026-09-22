"""
Inspect Function Signatures

-
"""

__all__: list[str] = [
    "validate_signature",
]

# IDEA: move to brick.call??

from collections.abc import Callable
from inspect import Parameter, Signature, signature
from typing import Literal

type Level = Literal[1, 2, 3, 4]


def validate_signature(
    func: Callable, baseline: Signature, level: Level = 1
) -> Signature | None:
    """
    Validate Function Signature against Baseline up to Strictness Level

    Level 1: Arity Check. Do they have the same number of parameters?
    Level 2: Structural Check. Do the parameter names match in exact order?
    Level 3: Kind Check. Do positional/keyword/var bindings match exactly?
    Level 4: Type Check. Do the annotations match (if baseline enforces them)?
    """

    if not callable(func):
        return None
    try:
        new_sig: Signature = signature(func)
    except ValueError, TypeError:
        return None

    checks: list[Callable[[Signature, Signature], bool]] = [
        _sig_check_1,
        _sig_check_2,
        _sig_check_3,
        _sig_check_4,
    ]
    return (
        new_sig
        if all(check(new_sig, baseline) for check in checks[0:level])
        else None
    )


def _sig_check_1(new_sig: Signature, base_sig: Signature) -> bool:
    """L1: Arity Check. Do they have the same number of parameters?"""
    return len(new_sig.parameters) == len(base_sig.parameters)


def _sig_check_2(new_sig: Signature, base_sig: Signature) -> bool:
    """L2: Structural Check. Do the parameter names match in exact order?"""
    return tuple(new_sig.parameters.keys()) == tuple(
        base_sig.parameters.keys()
    )


def _sig_check_3(new_sig: Signature, base_sig: Signature) -> bool:
    """L3: Kind Check. Do positional/keyword/var bindings match exactly?"""
    return all(
        n_param.kind == b_param.kind
        for n_param, b_param in zip(
            new_sig.parameters.values(),
            base_sig.parameters.values(),
            strict=True,
        )
    )


def _sig_check_4(new_sig: Signature, base_sig: Signature) -> bool:
    """L4: Type Check. Do the annotations match (if baseline enforces them)?"""
    for n_param, b_param in zip(
        new_sig.parameters.values(), base_sig.parameters.values(), strict=True
    ):
        if b_param.annotation is not Parameter.empty:
            if n_param.annotation != b_param.annotation:
                return False
    return True
