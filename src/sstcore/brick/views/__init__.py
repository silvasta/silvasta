"""
Atomize the Views to Single Methods for precise Selection

- Cli, Log, Repr, Rich, Str: provide stable Mixin catalog
  - Enums with a range of selected mixins

- ViewCatalog: Combine all mixin catalogs

- ViewMixins: provide all mixins classes with single __dunder__
  - all catalogue member plus any other implemented mixin


ViewCatalog:
+ Enum : Implemented Mixin Method
- Cli  : __cli__
- Str  : __str__
- Rich : __rich__
- Repr : __repr__
- Log  : __log__
                                   DependencyLevel.sstcore.brick[4]
"""

__all__: list[str] = [
    "ViewCatalog",
    "Cli",
    "Str",
    "Rich",
    "Repr",
    "Log",
    "catalog",  # TEST: which works better?
    #
    "ViewMixins",
    "cli",
    "str",
    "rich",
    "repr",
    "log",
]

# TASK: dependency level, then check where to export in brick

from types import SimpleNamespace

from ._catalog import Cli, Log, Repr, Rich, Str, ViewMixins


class ViewCatalog:  # LATER: attach better
    Cli = Cli
    Log = Log
    Repr = Repr
    Rich = Rich
    Str = Str


# TEST:
catalog = SimpleNamespace(  # IMPORTANT: approach 2
    # NOTE: first impression, typing completely gone...
    # NamedTuple?
    Cli=Cli,
    Log=Log,
    Repr=Repr,
    Rich=Rich,
    Str=Str,
)
