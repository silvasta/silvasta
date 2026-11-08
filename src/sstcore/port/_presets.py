"""
Group PreSets as Classes and Merge them to Modules

- bundle loose preset data for the different port modules
- belongs to their corresponding port module, import from there, not from here!

                                                 DependencyLevel[-]
"""  # TODO:

__all__: list[str] = [
    "AnnotationPresets",
    "LinkPresets",
]


from .structures import PresetMeta


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
