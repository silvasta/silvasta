"""
Meta Construction - Design the Skeleton of Classes

- StaticFuncMetaData: Convert methods to staticmethods and attach Views

"""

__all__: list[str] = [
    "StaticFuncMeta",
    "StaticFuncMetaData",
]
from ._static_toolkit import StaticFuncMeta, StaticFuncMetaData
