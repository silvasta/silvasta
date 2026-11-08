"""
Extracted from port.raising - the DTO/Spec/Input part

-
"""

from dataclasses import dataclass
from typing import Any, Self, TypedDict, Unpack

from ..raising import Raiser


class ErrorInput(TypedDict, total=False):
    # IDEA: create better pairs, improve:
    # - expected={"policy": PolicyEnum},
    # - received={"policy": policy},
    #   -> only 1 key for 2 values needed, avoid duplication and mismatches!
    # - Build some kind of ErrorComparisonRegistry that accepts[ManyInput]
    """Define the Kwarg Space of the Error Pipeline"""

    text: str
    expected: dict
    received: dict


@dataclass(frozen=True)  # CHECK: dataclass from __subclass_int__?
class ErrorSpec:
    """Define the Arg Space of the Internal Pipeline"""

    reason: Raiser
    text: str = ""
    expected: dict[str, Any] | None = None
    received: dict[str, Any] | None = None

    extra: dict[str, Any] | None = None  # CHECK: can here something change?

    __pos_fields__: tuple[str, ...] = ()

    def __str__(self):
        return f"{type(self).__name__}[{self.reason}]"

    def __repr__(self):
        log: str = "-|-".join(f"{k}:={v}" for k, v in vars(self).items())
        return f"{self}({log})"

    @classmethod
    def absorb(
        cls, reason: Raiser, /, *args, **kwargs: Unpack[ErrorInput]
    ) -> Self:
        """Extract the ErrorInput kwargs to form the ErrorSpec"""

        items: dict[str, Any] = {}
        extra: dict[str, Any] = {}

        pos_names: tuple[str, ...] = cls.__pos_fields__

        for name, val in zip(pos_names, args, strict=False):
            items[name] = val

        if len(args) > len(pos_names):
            extra["args"] = args[len(pos_names) :]

        _valid_fields = cls.__dataclass_fields__.keys()

        for key, value in kwargs.items():
            if key in _valid_fields:
                items[key] = value
            else:
                extra[key] = value

        return cls(reason=reason, extra=extra or None, **items)
