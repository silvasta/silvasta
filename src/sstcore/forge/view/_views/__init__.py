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
    "cli",
    "string",
    "rich",
    "repr",
    "log",
]


from . import _cli as cli
from . import _log as log
from . import _repr as repr
from . import _rich as rich
from . import _str as string
