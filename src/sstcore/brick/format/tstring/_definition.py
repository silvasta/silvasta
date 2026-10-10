"""
T-string Protocols

- TEMPORARY here, waiting for module in port

"""

from string.templatelib import Interpolation
from typing import Protocol

from ....port.calling import Richable, Stringable


class ViewTable(Protocol):
    def resolve(self, registered_cls: type, /) -> ViewRender | None: ...


class ViewRender(Protocol):
    def __call__(self, value: Stringable, item: Interpolation) -> Richable: ...
