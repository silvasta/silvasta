"""
Shape the Behaviour and Representation of the Global ...

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
"""

# TODO: module name
# IDEAS:
# - strict
# - reliable
# - define
# - govern

__all__: list[str] = [
    "Index",
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


class Index(BaseEnum):
    """Define the Axis for the {0..N} Members"""


class Machine(EnumView):
    """Task Executor"""


class Policy(BaseEnum):
    """Task Toggle"""


# TODO: PolicyDescriptor


class Option(BaseEnum):
    """Multiple Selections - Always 1 default (on zero)"""


class PrintOption(Option):
    """(Randomly) toggle views until it looks nice"""


class Catalog(BaseEnum):
    """Foolproof Selection"""


class MixinCatalog(BaseEnum):
    """Select without Surprise"""


# TODO: ViewOption?


class StateGraph(EnumView):
    """Static Decision Tool"""


class Transition(EnumView):
    """Dynamic Decision Tool"""
