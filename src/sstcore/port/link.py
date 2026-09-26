"""
Reference the Implementations back to their Definitions in the port

- Link and Sync docstrings at import time
  - Use docstring from sstcore.port as Single-Source-of-Truth (SSoT)
  - Append optional local docstring with implementation details

- Provide simple IDE navigation hook like in nvim: 'gd'

- Trigger static type checker warning on implementation mismatch

"""

__all__: list[str] = [
    "portlink",
    "PortLinker",
]

import typing as _t
from inspect import cleandoc as _cleandoc


class PortLinker[C, P](_t.Protocol):
    def __call__(self, cls: type[C & P]) -> type[C]:  # ty:ignore (type intersection)
        """Accept class C iff C implements P and return C unchanged"""


def portlink[C, P](protocol: type[P], /) -> PortLinker[C, P]:
    """Anchor an Implementation to its Protocol"""

    def wrapper(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
        """Merge docstrings and enforce static type check"""

        # IMPORTANT: what about the cls.__doc__? from protocol.__doc__??

        for attr_name in _t.get_protocol_members(protocol):
            if (
                (proto_attr := _reflect(protocol, attr_name))
                and (proto_doc := _extract_doc(proto_attr))
                and (cls_attr := _reflect(cls, attr_name))
            ):
                combined_doc: str = (
                    proto_doc
                    if not (cls_doc := _extract_doc(cls_attr))
                    else _merge(proto_doc, cls_doc)
                )
                _update_doc(cls_attr, combined_doc)

        return cls

    return wrapper


#  LINE: -- Internal Processing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _extract_doc(target: _t.Any, /) -> str:
    return (
        _cleandoc(doc)  #
        if (doc := getattr(target, "__doc__", None))
        else ""
    )


# REMOVE: before finish
def _outdated_reflect(target: type, /, attr_name: str) -> _t.Any | None:
    return (
        attr  #
        if callable(attr := getattr(target, attr_name, None))
        else None
    )


# AI_QUESTION: what about descriptors?
def _reflect(cls: type, name: str, /) -> _t.Any | None:
    """Extract attribute and handle special cases"""
    return (
        attr.__func__
        if isinstance((attr := _get(cls, name)), (classmethod, staticmethod))
        else attr
        if callable(attr) or isinstance(attr, property)
        else None
    )


# REMOVE: before finish
def _rejected_get(cls: type, name: str) -> _t.Any | None:
    """The MRO pipeline upwards is essential for Proto and Cls!"""
    return cls.__dict__.get(name)


def _get(cls: type, name: str) -> _t.Any | None:
    return getattr(cls, name, None)


class _Merger(_t.Protocol):
    def __call__(self, source: str, target: str, /) -> str:
        """Define format rule that concatenates two docstrings"""


# AI_TASK: make this customizable
def _default_merge(source: str, target: str) -> str:
    return f"""{source}\n\n[Implementation Notes]\n{target}"""


def _merge(proto_doc: str, cls_doc: str, merge: _Merger | None = None) -> str:
    return (
        cls_doc
        if proto_doc in cls_doc
        else (merge or _default_merge)(proto_doc, cls_doc)
    )


def _update_doc(attr: _t.Any, doc: str, /) -> None:
    """Safely inject the doc"""
    try:
        attr.__doc__ = doc
    except AttributeError, TypeError:
        return


# LINE: -- To be Considered! -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# NEXT: configuration, bind portlink with different merge format
class _Setup:
    """
    Idea:

    # later, without touching portlink's signature
    @portlink.using(join=my_join)(SomeProtocol)
    class Impl: ...

    link = portlink.using(join=my_join)
    @link(SomeProtocol)
    class Impl: ...
    """

    notes = "[Implementation Notes]"
    join: _Merger = staticmethod(
        lambda src, dst: f"{src}\n\n{_Setup.notes}\n{dst}"
    )
