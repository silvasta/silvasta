"""
New slim setup

-
"""

from dataclasses import dataclass
from inspect import _ParameterKind
from typing import Any

from ...port.casting import LspViolation
from ...port.empty import VOID, MayNot
from .. import reflect
from . import _lsp
from ._signature import SigVar

type Buckets = dict[_ParameterKind, list[SigVar]]
type SigVars = tuple[SigVar, ...]


@dataclass(frozen=True, slots=True)
class SigSpec:
    pos: SigVars = ()
    both: SigVars = ()
    args: SigVars = ()
    key: SigVars = ()
    kwargs: SigVars = ()

    result: Any = VOID

    is_async: bool = False
    is_generator: bool = False
    binding: reflect.sig.Binding = reflect.sig.Binding.FUNC
    tolerance: LspViolation = LspViolation.ZERO

    def allows(
        self,
        other: SigSpec,
        tolerance: MayNot[LspViolation] = None,
    ) -> bool:
        """Check whether `other` may substitute `self` under tolerance."""
        limit: LspViolation = self.tolerance if tolerance is None else tolerance
        return _lsp.allows(self, other, tolerance=limit)

    def diff(
        self,
        other: SigSpec,
        *,
        ignore: LspViolation = LspViolation.ZERO,
    ) -> LspViolation:
        """Compute all LSP violations when replacing `self` with `other`."""
        return _lsp.evaluate(self, other, ignore=ignore)
