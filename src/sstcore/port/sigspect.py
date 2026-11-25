"""
Define the Shape and Rules of the Input/Output Cast and Inspect

-
"""

import enum as _e
from collections.abc import Mapping
from inspect import _empty as EMPTY  # noqa:N812
from inspect import _ParameterKind
from typing import Any, Protocol, Self

from ._modulepath import ModulePath
from .empty import MayNot
from .primitives import ExplainedTuple
from .primitives._format import SpecParse
from .structures import DataClass, EnumField


class LspViolation(_e.IntFlag):
    """Categorize different Levels of LSP Violations"""

    explain = EnumField[ExplainedTuple[Any]].imports(
        path=ModulePath.parse(
            "sstcore.brick.call._lsp_detail:explain_lsp_violation",
        ),
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
    POS_KW_COLLISION = _e.auto()

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
        | REDUCED_MAX_POS
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


class SigVariable(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def kind(self) -> _ParameterKind: ...
    @property
    def has_default(self) -> bool: ...
    @property
    def annotation(self) -> Any: ...
    def evolve(
        self,
        *,
        name: MayNot[str] = None,
        kind: MayNot[_ParameterKind] = None,
        default: Any = EMPTY,
        annotation: Any = EMPTY,
    ) -> Self: ...


class SigSpecing(DataClass, Protocol):
    """Read-only signature contract required by LSP rule evaluators."""

    @property
    def pos(self) -> tuple[SigVariable, ...]: ...
    @property
    def both(self) -> tuple[SigVariable, ...]: ...
    @property
    def args(self) -> tuple[SigVariable, ...]: ...
    @property
    def key(self) -> tuple[SigVariable, ...]: ...
    @property
    def kwargs(self) -> tuple[SigVariable, ...]: ...
    @property
    def result(self) -> Any: ...
    @property
    def is_async(self) -> bool: ...
    @property
    def is_generator(self) -> bool: ...
    @property
    def binding(self) -> Any: ...

    @property
    def positionals(self) -> tuple[SigVariable, ...]: ...
    @property
    def keyword_map(self) -> Mapping[str, SigVariable]: ...
    @property
    def both_indices(self) -> Mapping[str, int]: ...
    @property
    def min_pos_only(self) -> int: ...
