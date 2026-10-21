"""
Meta Construction - Design the Layouts for Classes

FunctorMeta: Heavy Functional Executor
- FunctorMetaData

StaticFuncMeta: Static Methods Toolkit
- StaticFuncMetaData

Components
- ClsViewBase and ClsViewData: attach __{cli|log|rich|repr|str}__(cls)

Resolve
- combine_metas: merge potentially conflicting meta bases

"""

__all__: list[str] = [
    # func
    "FunctorMeta",
    "FunctorMetaData",
    # static
    "StaticFuncMeta",
    "StaticFuncMetaData",
    # components
    "ClsViewBase",
    "ClsViewData",
    # base
    "SstMeta",
    "SstMetaData",
    # resolve
    "combine_metas",
]

from ._functor import FunctorMeta, FunctorMetaData
from ._meta_base import SstMeta, SstMetaData
from ._meta_view import ClsViewBase, ClsViewData
from ._resolve import combine_metas
from ._static_func import StaticFuncMeta, StaticFuncMetaData
