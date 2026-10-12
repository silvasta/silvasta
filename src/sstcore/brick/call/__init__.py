"""
brick.call

- Callable Fragments
- Func input ensured

"""

__all__: list[str] = [
    "just_return",
    "validate_signature",
    #
    "ArgCaster",
    "ArgCast",
    "castarg",
]

from ._cast import ArgCast, ArgCaster, castarg
from ._inspect import validate_signature
from ._some import just_return
