"""
Group PreSets as Classes and Merge them to Modules

- bundle loose preset data for the different port modules
- belongs to their corresponding port module, import from there, not from here!

                                                 DependencyLevel[2]
"""  # TODO:

__all__: list[str] = [
    "PresetMeta",  # NEXT: where to expose??
    "LinkPresets",
    "AnnotationPresets",
]


from typing import Any

from ._types import Types as _T  # noqa: N814
from ._types import _LockedClsMeta
from .primitives import HashedTuple


class PresetMeta(_LockedClsMeta):  # waiting for own module?
    def __new__(mcls, name: str, bases: _T.Bases, namespace: _T.NameSpace):
        """
        Convert Mutable Structures and lock everything possible

        - set  -> frozenset
        - list -> tuple
        - dict -> frozendict
        """
        frozen_items: dict[str, Any] = {
            key: HashedTuple.hash(value)
            for key, value in namespace.items()
            if not key.startswith("_")  # LATER: by toggle? (AttrFilter)
        }
        namespace.update(frozen_items)
        namespace.setdefault("__slots__", ())
        return super().__new__(mcls, name, bases, namespace)


class LinkPresets(metaclass=PresetMeta):
    DUNDERS: set[str] = {
        "__doc__",
        "__func__",
        "__portlinks__",
    }
    REFLECT: set[str] = {"detect", "collect", "project", "redact"}
    INIT: list[str] = ["__post_init__", "__init__"]


class AnnotationPresets(metaclass=PresetMeta):
    """
    Collect all Presets for the Typed Annotations:

    - Definition: port.annotate
    - Production: brick.call|reflect
    - Manufacture: forge.typed|any
    """

    DUNDERS: set[str] = {
        "__init__",
        "__new__",
        "__dict__",
        "__weakref__",
        "__doc__",
        "__module__",
        "__annotations__",
        "__subclasshook__",
    }
    CALLING: set[str] = {
        "__call__",
        "__getitem__",
        "__iter__",
        "__enter__",
        "__exit__",
    }
    PROTO_DUNDERS: set[str] = {
        "__call__",
        "__getitem__",
        "__iter__",
        "__enter__",
        "__exit__",
        "__next__",
        "__await__",
        "__aiter__",
        "__anext__",
    }
    PROTO_SUNDERS: set[str] = {
        "_is_protocol",
        "_is_runtime_protocol",
    }
