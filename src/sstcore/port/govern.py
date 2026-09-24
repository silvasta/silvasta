"""
Define the Shape and Behaviour of the relibale and strict Dispatcher

- First operational assembly of the definition and decision taker

                                                 DependencyLevel[1]
Strategy:
  Now
  - Index
  Soon
  - Machine
  - Policy
  Later
  - Option
  Final
  - SstEnum(Enum)
  Finally
    SstEnum

  - Overall: not to fast and not to deeply nested, step by step

"""

# TODO: module name
# IDEAS:
# - strict
# - reliable
# - define
# - govern

__all__: list[str] = [
    "EnumIndex",
    "EnumId",
    # base
    "BaseEnum",
    "EnumZero",
    # view
    "EnumRepr",
    "EnumStr",
    # TODO: "SstEnum",
]


from ._enum import EnumRepr, EnumStr, EnumZero

type EnumId[EnumT] = EnumT | str | int


class EnumView(EnumStr, EnumRepr): ...


class BaseEnum(EnumZero, EnumView):
    """Provide Base with Simple View and Modified Access"""


class EnumIndex(BaseEnum):
    """Define the Axis for the {0..N} Members"""


class EnumMachine(EnumView):
    # TASK: check class StubMachine(Machine):... here, for unique root
    """Task Executor"""


class PolicyEnum(BaseEnum):
    # TODO: PolicyDescriptor
    """Task Toggle"""


# IMPORTANT: MODE???
# IDEA: Mode??
# NOTE: Policy and Option, same or not?
# - mode inbetween or both together?
# - both still possible, keep it flexibel and don't get locked somewhere


class EnumMode(BaseEnum):
    """Task Toggle"""


class EnumOption(BaseEnum):
    """Multiple Selections - Always 1 default (on zero)"""


class PrintOption(EnumOption):
    """(Randomly) toggle views until it looks nice"""


# TODO: ViewOption? ViewEnumCatalog already exists (inirect)


class EnumCatalog(BaseEnum):
    """Foolproof Selection"""


class MixinCatalog(BaseEnum):
    """Select without Surprise"""


class StateGraph(EnumView):
    """Static Decision Tool"""


class Transition(EnumView):
    """Dynamic Decision Tool"""
