"""
Meta Construction - Design the Layouts for Classes

- StaticFuncMetaData: Convert methods to staticmethods and attach Views

"""

__all__: list[str] = [
    "StaticFuncMeta",
    "StaticFuncMetaData",
]
from ._static_func import StaticFuncMeta, StaticFuncMetaData
