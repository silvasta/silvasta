"""
MetaConstruction - Design the Skeleton of Classes

- StaticToolkitMeta: Convert methods to staticmethods and attach Views

"""

__all__: list[str] = [
    "StaticToolkitMeta",
    "ToolkitMetaArgs",
]
from ._static_toolkit import StaticToolkitMeta, ToolkitMetaArgs
