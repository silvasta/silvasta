"""
- where?

-
"""

__all__: list[str] = [
    # ""
]

import typing as _t
from typing import Any

from ..empty import VOID, MayBe


class BaseCaster[ArgT, OutT]:
    """
    Reusable orchestration base for ArgCasting implementations.

    Handles `VOID` / `default` target resolution (`aim`) and delegates to `cast_target`.
    """

    input_types: _t.ClassVar[type | tuple[type, ...]] = object

    def __init__(self, **kwargs: Any) -> None:
        self.default: Any = kwargs.pop("default", VOID)
        self.kwargs: dict[str, Any] = kwargs

    def __call__(
        self, target: MayBe[ArgT] = VOID, /, *, default: MayBe[OutT] = VOID
    ) -> OutT:
        selected = self.aim(target, default)
        return self.cast_target(selected)

    def aim(
        self, target: MayBe[ArgT], default: MayBe[OutT] = VOID
    ) -> ArgT | OutT | VOID:
        """Select target from incoming value, signature default, or caster default."""
        if target is VOID:
            return self.default if default is VOID else default
        if isinstance(target, self.input_types):
            return target
        return VOID

    def cast_target(self, target: ArgT | OutT | VOID, /) -> OutT:
        raise NotImplementedError
