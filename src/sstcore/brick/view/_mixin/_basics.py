"""
Provide shared utils for Mixins.

- str/rich or log/repr will need it

"""

__all__: list[str] = [
    "MixinSentinel",
    "data",
]

from typing import Any

from ....brick.format import reflect
from ....port.event.dto import CliDTO, LogDTO
from ....port.view import PydanticModel, RichRenderable


class MixinSentinel:
    """Imitate a Mixin to replace None in View selection pipeline"""

    def __cli__(self) -> CliDTO:
        raise NotImplementedError

    def __log__(self) -> LogDTO:
        raise NotImplementedError

    def __rich__(self) -> RichRenderable:
        raise NotImplementedError


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### (remaining) Extractor
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def data(_target: Any, *, exclude: set[str] | None = None) -> dict[str, Any]:
    """Extract public data filtered by exclude, dispatch for Pydantic"""

    exclude: set[str] = exclude or set()

    if isinstance(_target, PydanticModel):
        return _target.model_dump(exclude=exclude)

    return reflect.data(_target, exclude)
