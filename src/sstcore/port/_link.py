"""
Reference the Implementations back to their Definitions in the Port

- Distribute DocStrings from sstcore.port as Single-Source-of-Truth (SSoT)

"""

# LATER: find proper place for this implementation and define export location

import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

INCLUDES_DUNDER: tuple[str, ...] = (
    # LATER: extend for specific: __sst_dunders__
    "__call__",
    # IDEA: or just follow the Protocol?
    # - if a __dunder__ is in the Protocol, most likely with a purpose?
)


# AI: the slightly adapted original version
def implements[T](protocol: type) -> Callable[[T], T]:
    """
    Anchor an implementation to its Protocol

    - Provide simple IDE navigation hook like in Neovim: 'gd'
    - Link and Sync docstrings at import time
    """

    def wrapper(cls: T) -> T:
        for name in dir(protocol):
            if name.startswith("__") and name not in INCLUDES_DUNDER:
                continue

            # Checks on Protocol
            proto_attr: Any | None = getattr(protocol, name, None)
            # MERGE: V1: confusing getattr dominance
            if not callable(proto_attr) or not getattr(
                proto_attr, "__doc__", None
            ):
                continue
            # MERGE: V2: explicit step by step
            if not callable(proto_attr):
                continue
            if not getattr(proto_attr, "__doc__", None):
                # AI: any drawbacks of one more `if ...:continue` check?
                continue

            # Checks on Implementation
            cls_attr: Any | None = getattr(cls, name, None)
            if not cls_attr or not callable(cls_attr):
                continue

            # Clean and merge docstrings safely
            proto_doc: str = inspect.cleandoc(proto_attr.__doc__)
            cls_doc: str = getattr(cls_attr, "__doc__", "")
            cls_doc: str = inspect.cleandoc(cls_doc) if cls_doc else ""

            # Inject
            if not cls_doc:
                cls_attr.__doc__ = proto_doc
            elif proto_doc not in cls_doc:
                # prevent duplicate merging on hot-reloads
                cls_attr.__doc__ = (
                    f"{proto_doc}\n\n[Implementation Notes]\n{cls_doc}"
                )

        return cls

    return wrapper


#  LINE: -- Testing for: if TYPE_CHECKING:... -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#


# AI: failed tests inside the wrapper
def _portlink1[T, ProtoT](protocol: ProtoT) -> Callable[[T], T]:

    def wrapper(cls: T) -> T:

        # TEST: experiment 1: the naive TYPE_CHECKING
        # ... failed, T is TypeVar
        # if TYPE_CHECKING:
        #     _unit: ProtoT = T
        #     _cls: type[ProtoT] = T

        # TEST: experiment 2: assert
        if TYPE_CHECKING:
            assert ProtoT == T  # no effect at all

        for name in dir(protocol):
            _temp_extract_wrapper_logic(name, cls, protocol)

        return cls

    return wrapper


# AI: failed tests: casts the implementation class as protocol:
# - heavy failure: warns for impossible __init__() on implementation
def _portlink2[T](protocol: T) -> Callable[[T], T]:

    def wrapper(cls: T) -> T:
        for name in dir(protocol):
            _temp_extract_wrapper_logic(name, cls, protocol)

        return cls

    return wrapper


# STRATEGY: Definitions that must hold:
# - x: ProtoT = ClsT()
# - y: type[ProtoT] = ClsT


def portlink[ClsT, ProtoT](protocol: ProtoT) -> Callable[[ClsT], ClsT]:

    # AI_FOCUS: somewhere here must be the solution of the problem! (if it exists...)

    def wrapper(cls: ClsT) -> ClsT:
        for name in dir(protocol):
            _temp_extract_wrapper_logic(name, cls, protocol)

        return cls

    return wrapper


# IDEA: Generic Type that handles ClsT and ProtoT

# AI: failed tests: cannot process it and then casts implementation to protocol...
# │   ├╴  Argument is incorrect: Expected `<class 'OnlyForCheck'>`, found `<class 'CheckIfTypeCheckingGood'>` ty (invalid-argument-type) [48, 1]
# │   ├╴  Argument is incorrect: Expected `<class 'OnlyForCheck'>`, found `<class 'CheckIfTypeCheckingMissingSignature'>` ty (invalid-argument-type) [70, 1]
# │   ├╴  Argument is incorrect: Expected `<class 'OnlyForCheck'>`, found `<class 'CheckIfTypeCheckingBadTyping'>` ty (invalid-argument-type) [85, 1]
# │   ├╴  Cannot instantiate class `OnlyForCheck`: This call will raise `TypeError` at runtime ty (call-non-callable) [117, 40]
# │   ├╴  Cannot instantiate class `OnlyForCheck`: This call will raise `TypeError` at runtime ty (call-non-callable) [118, 40]
# │   ├╴  Cannot instantiate class `OnlyForCheck`: This call will raise `TypeError` at runtime ty (call-non-callable) [119, 40]

type ProjectedT[ClsT] = ClsT & Any  # AI: here maybe the magic trick?
# INFO: on type intersection: Python3.14+, warnings from ty:
# └╴  port/  1
#   └╴󰌠  _link.py  1
#     └╴  Intersection type syntax is experimental ty (experimental-syntax) [133, 25]


def _portlink3[ClsT](protocol: ProjectedT[ClsT]) -> Callable[[ClsT], ClsT]:

    # INFO: result
    def wrapper(cls: ClsT) -> ClsT:
        for name in dir(protocol):
            _temp_extract_wrapper_logic(name, cls, protocol)

        return cls

    return wrapper


# AI: failed tests: no issue for all decorators, but should flag class 2 and class 3...
type MixedT[C, P] = type[C & P]


def _portlink4[ClsT, ProtoT](
    protocol: ProtoT, _dummy: MixedT[ClsT, ProtoT] | None = None
) -> Callable[[ClsT], ClsT]:

    def wrapper(cls: ClsT) -> ClsT:
        for name in dir(protocol):
            _temp_extract_wrapper_logic(name, cls, protocol)

        return cls

    return wrapper


#  LINE: -- helper -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _temp_extract_wrapper_logic(name, cls, protocol):
    """Help to avoid blowing up the copies below"""
    if name.startswith("__") and name not in INCLUDES_DUNDER:
        return

    # Checks on Protocol
    proto_attr: Any | None = getattr(protocol, name, None)
    # MERGE: V1: confusing getattr dominance
    if not callable(proto_attr) or not getattr(proto_attr, "__doc__", None):
        return

    # Checks on Implementation
    cls_attr: Any | None = getattr(cls, name, None)
    if not cls_attr or not callable(cls_attr):
        return

    # Clean and merge docstrings safely
    proto_doc: str = inspect.cleandoc(proto_attr.__doc__)
    cls_doc: str = getattr(cls_attr, "__doc__", "")
    cls_doc: str = inspect.cleandoc(cls_doc) if cls_doc else ""

    # Inject
    if not cls_doc:
        cls_attr.__doc__ = proto_doc
    elif proto_doc not in cls_doc:
        # prevent duplicate merging on hot-reloads
        cls_attr.__doc__ = f"{proto_doc}\n\n[Implementation Notes]\n{cls_doc}"
