"""
Signature Inspection with LSP checks and renderings

- Callable Fragments
- Func input ensured

                          DependencyLevel.sstcore.brick.call[1.1:0]
"""

__all__: list[str] = [
    "SigVar",
    "SigSpec",
    # checks
    "LspRules",
    "evaluate",
    "allows",
    "check_param_variance",
    "check_return_variance",
    # algebra
    "subtract",
    "intersect",
    "union",
    # data table
    "explain_lsp_violation",
]

from ._algebra import intersect, subtract, union
from ._explain import explain_lsp_violation
from ._rules import (
    LspRules,
    allows,
    check_param_variance,
    check_return_variance,
    evaluate,
)
from ._sigspec import SigSpec, SigVar
