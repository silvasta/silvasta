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

        for attr_name in _scan_attrs(protocol):
            if (
                (proto_attr := _reflect(protocol, attr_name))
                and (proto_doc := _inspect(proto_attr))
                and (cls_attr := _reflect(cls, attr_name))
            ):
                cls_attr.__doc__ = (
                    proto_doc
                    if not (cls_doc := _inspect(cls_attr))
                    else _merge(proto_doc, cls_doc)
                )

        return cls

    return wrapper


#  LINE: -- Internal Processing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _scan_attrs(target: type, /, ignore: tuple | None = None) -> set[str]:
    if ignore is None:  # LATER: make this customizable at caller
        ignore: tuple = (object, _t.Protocol, _t.Generic)
    return {
        proto_attr_name
        for base in target.__mro__
        if base not in ignore
        for proto_attr_name in base.__dict__.keys()
    }


def _inspect(target: _t.Any, /) -> str:
    return (
        _cleandoc(doc)  #
        if (doc := getattr(target, "__doc__", None))
        else ""
    )


def _reflect(target: type, /, attr_name: str) -> _t.Any | None:
    return (
        attr  #
        if callable(attr := getattr(target, attr_name, None))
        else None
    )


def _merge(proto_doc: str, cls_doc: str, merge: _Merger | None = None) -> str:
    return (
        cls_doc
        if proto_doc in cls_doc
        else (merge or _merger)(proto_doc, cls_doc)
    )


class _Merger(_t.Protocol):
    def __call__(self, source: str, target: str, /) -> str:
        """Define format rule that concatenates two docstrings"""


def _merger(source: str, target: str) -> str:  # LATER: make this customizable
    return f"""{source}\n\n[Implementation Notes]\n{target}"""
