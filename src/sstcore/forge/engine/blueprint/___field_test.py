"""
Assemble Class Based Descriptors

- EXPERIMENTAL
                                                 DependencyLevel[2]
"""

__all__: list[str] = [
    # "",
]
from enum import Enum

from ....brick.field._meta import MetaStateField
from ._static_func import StaticFuncMeta


class _RenderState(Enum):
    """COPY!!!"""

    INIT = "init"
    PREP = "prep"
    DRAW = "draw"
    CLEAN = "clean"
    ERROR = "error"


_VALID_TRANSITIONS = {
    _RenderState.INIT: {_RenderState.PREP, _RenderState.ERROR},
    _RenderState.PREP: {_RenderState.DRAW, _RenderState.ERROR},
    _RenderState.DRAW: {_RenderState.CLEAN, _RenderState.ERROR},
    _RenderState.CLEAN: {_RenderState.INIT},
    _RenderState.ERROR: {_RenderState.INIT},  # Requires a reset to recover
}


def _transit(
    unit: object, current: _RenderState, next: _RenderState, **kwargs
):
    return next in _VALID_TRANSITIONS.get(current, set())


class StatefulStaticMeta(StaticFuncMeta):
    # The descriptor lives on the metaclass
    state = MetaStateField(
        transition=_transit, types=_RenderState, default=_RenderState.INIT
    )


class RenderMachine(metaclass=StatefulStaticMeta):
    # Static methods can now read/react to cls.state
    @classmethod
    def process(cls):
        if cls.state != _RenderState.PREP:
            raise RuntimeError("Pipeline not prepped!")


RenderMachine.state = _RenderState.PREP
RenderMachine.process()
RenderMachine.state = _RenderState.CLEAN
RenderMachine.process()
