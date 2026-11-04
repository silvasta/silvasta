"""
Group PreSets as Classes and Merge them to Modules

- bundle loose preset data for the different port modules
- belongs to their corresponding port module, import from there, not from here!

                                                 DependencyLevel[-]
"""

__all__: list[str] = [
    "AnnoPresets",
    "anno_presets",
    "PresetMeta",
]

from typing import Any, Never

from ._frozen import HashedTuple

# LATER: meta assembly
# - make the body in __new__ selectable by class.__init__ arg
# - like index or Literal to select level
# NEXT: decide if use as Cls or as Unit


class PresetMeta(type):
    """Combine Utils and SafetyTools for Presets"""

    def __new__(mcls, name, bases, namespace):
        """Attach all sets as frozensets"""  # LATER: maybe more

        frozen_items: dict[str, Any] = {
            key: frozenset(value)
            for key, value in namespace.items()
            if isinstance(value, set)
        }
        namespace.update(frozen_items)

        return super().__new__(mcls, name, bases, namespace)


class _PresetMeta(type):  # Max Freeze
    """
    Deep-freeze Preset namespaces and lock against runtime mutation

    - Automatically converts:
      - set  -> frozenset
      - list -> tuple
      - dict -> frozendict
    """

    def __new__(
        mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ):
        frozen_items: dict[str, Any] = {
            key: HashedTuple.hash(value)
            for key, value in namespace.items()
            if not key.startswith("_")
        }
        namespace.update(frozen_items)
        namespace.setdefault("__slots__", ())
        return super().__new__(mcls, name, bases, namespace)

    def __setattr__(cls, name: str, _value: Any) -> Never:
        raise AttributeError(f"Preset '{cls.__name__}.{name}' is read-only")

    def __delattr__(cls, name: str) -> Never:
        raise AttributeError(f"Preset '{cls.__name__}.{name}' is read-only")


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class AnnoPresets(metaclass=PresetMeta):
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


anno_presets = AnnoPresets()
