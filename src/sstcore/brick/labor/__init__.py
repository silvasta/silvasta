"""
Provide pure functional fragments ready to use or assemble

- Detect, Inspect, Neglect, Modify, whatever...

"""

# STRATEGY: Catalog->Functor->Toolbox

__all__: list[str] = [
    # single
    "clsname",
    "just_return",
    # modules
    "mro_calc",  # IDEA: maybe mro package, beside calc a lot of other operations wait (maybe will stay in compose)
    #
    "reflect",
    "inject",
    #
    "transform",  # RENAME:
]

# IDEA: Expose
# instead of pushing too much single function here,
# - just create a public module all?
# from sstcore.brick.labor.all import any_desired
# - other option is exposing all modules here but,
#   1 public module per private module (at least the important)
# NEXT: even better! subpackages!
# - subpackages bind other modules and provide __init__ expose
# With smart naming, organization and structure:
# - build nested interchangeable trees with high gain and less effort
#   (except a lot of files...)

from . import _inject as inject
from . import _mro as mro_calc
from . import _reflect as reflect
from . import _transform as transform
from ._reflect import clsname, just_return
