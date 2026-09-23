"""
StubTyper as the Head of the Writers

                                                 DependencyLevel[0]
"""

from typing import TYPE_CHECKING

__all__: list[str] = [
    "StubTyper",
]


from ...port.shape import Typer
from ._engine import StubFileMachine


class StubTyper[**P]:
    """Spin up the universal typed writing Framework"""

    def schema(self) -> dict[str, list[str]]:
        """Generate Layer Mapping as SSoT for Stub typing"""
        raise NotImplementedError

    def draw(self, *args: P.args, **kwargs: P.kwargs): ...
    def start(self) -> list[str]:
        ...
        return StubFileMachine.run()


if TYPE_CHECKING:
    _unit: Typer = StubTyper()
    _cls: type[Typer] = StubTyper


class StackTyper[**P]: ...
