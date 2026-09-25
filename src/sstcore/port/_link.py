"""
Reference the Implementations back to their Definitions in the Port

- Distribute DocStrings from sstcore.port as Single-Source-of-Truth (SSoT)

"""

# LATER: find proper place for this implementation and define export location

import inspect
from collections.abc import Callable
from typing import Any, Generic, Protocol

type Simply[T] = Callable[[T], T]


def implements[T: type](protocol: type) -> Simply[T]:
    # WARN: check if T:type cannot override somethig!
    """
    Anchor an implementation to its Protocol

    - Provide simple IDE navigation hook like in Neovim: 'gd'
    - Link and Sync docstrings at import time
    """

    def wrapper(cls: T) -> T:
        _link_docstrings(protocol, cls)
        return cls

    return wrapper


class _PortlinkDecorator1[P](Protocol):
    """Decorator object: accept class C iff C implements P; return C unchanged."""

    def __call__[C: P](self, cls: type[C]) -> type[C]: ...


def _portlink1[P](protocol: type[P]) -> _PortlinkDecorator1[P]:
    """Anchor an implementation to a Protocol.

    Static: flag missing/wrong members (same as ``x: P = Impl()``).
    Runtime: merge protocol docstrings. Does not recast Impl to P.
    """

    def wrapper[C: P](cls: type[C]) -> type[C]:
        _link_docstrings(protocol, cls)
        return cls

    return wrapper


class _PortlinkDecorator[C, P](Protocol):
    """Decorator object: accept class C iff C implements P; return C unchanged."""

    def __call__(self, cls: type[C & P]) -> type[C]: ...  # ty:ignore


def portlink[C, P](protocol: type[P]) -> _PortlinkDecorator[C, P]:
    # AI: This looks very promising!
    # - Correctly flagged Check1 as fine
    # - Correctly flagged Check2,Check3 as fail

    def wrapper(cls: type[C & P]) -> type[C]:  # ty:ignore
        _link_docstrings(protocol, cls)
        return cls

    return wrapper


def _portlink2[C, P](protocol: type[P]) -> Simply[C]:
    # AI: Test for even more simple setup:
    # - Fail: no warnings at all

    def wrapper(cls: type[C & P]) -> type[C]:  # ty:ignore
        _link_docstrings(protocol, cls)
        return cls

    return wrapper


#  LINE: -- Internal Processing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _link_docstrings(protocol: type, cls: type) -> None:
    """Merge Protocol docs to Callable Attributes of cls"""

    valid_names: set[str] = set()
    for base in protocol.__mro__:
        if base in (object, Protocol, Generic):
            continue
        valid_names.update(base.__dict__.keys())

    for name in valid_names:
        proto_attr: Any | None = getattr(protocol, name, None)
        proto_doc: str | None = getattr(proto_attr, "__doc__", None)
        if not callable(proto_attr) or not proto_doc:
            continue

        cls_attr: Any | None = getattr(cls, name, None)
        if not cls_attr or not callable(cls_attr):
            continue

        proto_doc: str = inspect.cleandoc(proto_attr.__doc__)
        cls_doc: str = getattr(cls_attr, "__doc__", "")
        cls_doc: str = inspect.cleandoc(cls_doc) if cls_doc else ""

        if not cls_doc:
            cls_attr.__doc__ = proto_doc
        elif proto_doc not in cls_doc:
            final_doc = f"{proto_doc}\n\n[Implementation Notes]\n{cls_doc}"
            cls_attr.__doc__ = final_doc
