"""
Meta Construction - Design the Layouts for Classes

- FunctorMeta: Heavy Functional Executor
- ...Data: ...

- StaticFuncMeta: StaticMethods Toolkit
- ...Data: mainly the views...

"""

# STRATEGY: split the cls-views to base meta

__all__: list[str] = [
    # func
    "FunctorMeta",
    "FunctorMetaData",
    # static
    "StaticFuncMeta",
    "StaticFuncMetaData",
]

from ._functor import FunctorMeta, FunctorMetaData
from ._static_func import StaticFuncMeta, StaticFuncMetaData
