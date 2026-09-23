"""
Extract Type Information from Protocols and Classes for Stub Generation

- Execute functional stack together with Class Builder and Meta Constructors


                      DependencyLevel.sstcore.forge.engine.typed[0]
"""

__all__: list[str] = [
    "ForgeTyper1",
    "ForgeTyper2",
]

from collections.abc import Callable
from typing import TYPE_CHECKING

from ....brick.labor import clsname
from ....port.shape import Typer
from ....port.stacking import StackingCore
from ..blueprint import StaticFuncMeta, StaticFuncMetaData
from . import ___typed_well as _w
from . import _extract as _e
from . import _render as _r
from . import _types as _t
from ._extract import extract_members
from ._render import render_protocol_stub


class ForgeTyper1:
    """
    Functional adapter that bridges protocol extraction to the Typer protocol.

    Each classmethod accepts a protocol or class and returns ready-to-write
    stub text.  This is the primary entry point for forge.engine consumers
    that need typed output without depending on util.write.
    """

    @classmethod
    # IDEA: StrategyFiled? switch the draws
    def draw(cls, source: type, *, name: str = "") -> str:
        """Render a full class stub from a Protocol or regular class."""
        return render_protocol_stub(source, name=name)

    @classmethod
    def members(cls, source: type) -> list[_t.PublicMember]:
        """Expose extracted members for downstream consumers (Builder, Meta)."""
        return extract_members(source)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --

ForgeTyperMetaInput = StaticFuncMetaData(
    name=lambda cls: f" 🛠️{clsname(cls)} 🛠️"
)


class ForgeTyper2(metaclass=StaticFuncMeta, data=ForgeTyperMetaInput):
    """Façade over the functional stack. Safe to hand to Builder/Meta."""

    members: Callable = _w.protocol_members
    render: Callable = _w.render_class
    draw: Callable = _w.draw_protocol


if TYPE_CHECKING:
    _typer: Typer = ForgeTyper2()

#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#


class StackTyper:
    """Smart generator converting StackingCore instances into typed call-chains."""

    @classmethod
    def render(cls, core: StackingCore, class_prefix: str) -> str:
        """Convert a StackingCore into a fluent chain-state stub class definition."""

        return _r.synthesize_fluent_code(
            prefix=class_prefix,
            schema=core.schema(),
            call_signature=_e.extract_call_signature(core.call),
        )
