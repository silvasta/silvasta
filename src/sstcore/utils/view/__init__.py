"""
Shape the View of the Classes

- view: attach configurable view to the decorated class
- ViewBuilder: store one view combination for Mixin composition
- Cli, Log, Repr, Rich, Str: provide category Mixin selection

"""

__all__: list[str] = [
    "view",
    "ViewBuilder",
    # enums
    "Cli",
    "Str",
    "Rich",
    "Repr",
    "Log",
]


from .compose import ViewBuilder, view
from .registry import Cli, Log, Repr, Rich, Str
