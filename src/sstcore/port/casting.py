"""
Define the Shape and Rules of the Input/Output Caster

-
"""

import enum as _e
from typing import Any

from ._modulepath import ModulePath
from .primitives import ExplainedTuple
from .primitives._format import SpecParse
from .structures import EnumField


class LspViolation(_e.IntFlag):
    """Categorize different Levels of LSP Violations"""

    explain = EnumField[ExplainedTuple[Any]].imports(
        path=ModulePath.parse(
            "sstcore.brick.call._lsp:explain_lsp_violation",
        ),
        # AI_TASK: here the wiring of ExplainedTuple.combine messed up...
        # - find a solution that works just like here below
        fallback=ExplainedTuple.combine,
        cache_fallback=True,
    )

    ZERO = 0

    # Positional
    POS_ONLY_RENAMED = _e.auto()
    DROPPED_VAR_POS = _e.auto()
    REDUCED_MAX_POS = _e.auto()
    INCREASED_MIN_POS = _e.auto()

    # Keyword / Binding Vectors
    DROPPED_VAR_KW = _e.auto()
    LOST_KW_ACCESS = _e.auto()
    LOST_POS_ACCESS = _e.auto()
    DROPPED_KW_NAME = _e.auto()
    ADDED_REQUIRED_KW = _e.auto()

    # Parameter Types (Contravariance)
    ADDED_PARAM_CONSTRAINT = _e.auto()
    NARROWED_PARAM_TYPE = _e.auto()
    DISJOINT_PARAM_TYPE = _e.auto()

    # Return Types (Covariance)
    WIDENED_RETURN_SUPERSET = _e.auto()
    OVERLAPPING_RETURN_UNION = _e.auto()
    DISJOINT_RETURN_TYPE = _e.auto()

    # Execution Semantics
    SYNC_ASYNC_MISMATCH = _e.auto()
    GENERATOR_MISMATCH = _e.auto()
    DESCRIPTOR_BINDING_SHIFT = _e.auto()

    HOOK_PLUGIN = (
        POS_ONLY_RENAMED
        | DROPPED_VAR_POS
        | DROPPED_VAR_KW
        | ADDED_PARAM_CONSTRAINT
    )

    SINK_CALLBACK = (
        POS_ONLY_RENAMED
        | DROPPED_VAR_POS
        | DROPPED_VAR_KW
        | DROPPED_KW_NAME
        | WIDENED_RETURN_SUPERSET
        | OVERLAPPING_RETURN_UNION
        | DISJOINT_RETURN_TYPE
    )

    MORPHING_INCLUSIVE = (  # Original return type remains
        POS_ONLY_RENAMED | ADDED_PARAM_CONSTRAINT | WIDENED_RETURN_SUPERSET
    )

    MORPHING_ANY_RETURN = (  # Full transformation
        MORPHING_INCLUSIVE | OVERLAPPING_RETURN_UNION | DISJOINT_RETURN_TYPE
    )

    @property
    def bits(self) -> str:
        """Provide the Bit Representation (with Zeros and Ones)"""
        return f"{self:0{len(type(self))}b}"

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.bits}]::{self.name}[{self.value}]"

    def __rich__(self) -> Any:
        return self.explain.__rich__()

    def __format__(self, format_spec: str) -> str:
        # MOVE: close to ExplainedTuple.__format__? at least somewhere hidden
        match format_spec:
            case "b":
                return self.bits
            case spec if SpecParse.accepts(spec):
                return self.explain.__format__(spec)
            case _:
                if (
                    any(c in format_spec for c in "<>^")
                    and format_spec[-1] not in "bcdoxXn"
                ):
                    return format(str(self), format_spec)
                return super().__format__(format_spec)
