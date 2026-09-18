from collections.abc import Callable
from inspect import Signature, signature

from ....port.calling import Calling


def is_calculating[IsT](_object, _type: type, /, strict=False) -> TypeIs[IsT]:
    # REFACTOR:
    """
    Check if the _object's hello method has been morphed into a calculator.

    This inspects the actual runtime state of the object.
    """

    if not isinstance(_object, _type):
        return False
    if not hasattr(_object, "__dict__"):
        return False
    if "_hello_override" not in _object.__dict__:  # TODO: for check on self
        return False

    if not strict:
        return True

    # NEXT: signature checks
    from inspect import signature

    current_func: Calling = _object.__dict__["_hello_override"]  # TODO:
    sig: Signature = signature(current_func)
    # EXTRACT:
    params: list[str] = list(sig.parameters.keys())

    return len(params) >= 2 and params[1] == "amount"


# REMOVE: after impement finish
def _minimal_minimal(self, instance, value):
    if not callable(value):
        raise TypeError("Value must be callable.")


# REMOVE: after impement finish
def _minimal_sig_check(base_sig: Signature, new_func: Callable) -> bool:
    """IDEA: directly get signature back if check is ok?"""
    new_sig: Signature = signature(new_func)
    # if len(new_sig.parameters) != len(self.expected_sig.parameters):
    #     raise ValueError(
    #         f"Signature mismatch. Expected {len(self.expected_sig.parameters)} "
    #         f"parameters, got {len(new_sig.parameters)}."
    #     )
    return len(new_sig.parameters) == len(base_sig.parameters)


# MOVE: after impement finish, brick.labor.inspect
def _check_sig_param_length(sig1, sig2) -> bool:
    return len(sig1.parameters) == len(sig2.parameters)


# IDEA: like a catalog of
def _check_1() -> bool: ...  # ty:ignore
def _check_2() -> bool: ...  # ty:ignore
def _check_3() -> bool: ...  # ty:ignore


# MOVE: after impement finish, brick.labor.inspect
def _validated_sig(
    func: Callable, baseline: Signature | None = None
) -> Signature | None:
    new_sig: Signature = signature(func)
    if not baseline:  # LATER: what to check at single signature?
        return new_sig
    checks_ok: list[bool] = [  # LATER: build check box
        _check_sig_param_length(new_sig, baseline),
    ]
    return new_sig if all(checks_ok) else None
