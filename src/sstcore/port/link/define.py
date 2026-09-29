"""
Definitions

- temporary module
"""

import typing as _t

from .data import PlugDocs, PortDocs


class PortEmit[**P](_t.Protocol):
    def __call__(self, *arg: P.args, **kwarg: P.kwargs) -> None: ...


class PortLinker[C, P](_t.Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


class DocMerger(_t.Protocol):  # IDEA: Merging? only if as well operator
    def __call__(self, ports: PortDocs, plugs: PlugDocs) -> str:
        """Format and Render Protocol and Implementation docstrings"""


#  LINE: -- Operators -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Reflecting(_t.Protocol):
    def __call__(self, target: _t.Any, attr: str, /) -> _t.Any:
        """Extract the attribute value from the target"""


class Injecting(_t.Protocol):
    def __call__(self, target: _t.Any, value: _t.Any, /, attr: str) -> str:
        """Attach the new attribute value into the target"""


class Collecting(_t.Protocol):
    def __call__(self, port: type, plug: type, attr: str, /) -> _t.Any:
        """Harvest data in both sides MRO pipeline"""
