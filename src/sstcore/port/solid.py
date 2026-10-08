"""
Define the Shape and Behaviour of the Solid Objects

- Collect ideas for Concepts and possible Bases

                                    DependencyLevel.sstcore.port[1]
"""

__all__: list[str] = [
    # common
    "PolicyEnum",
    "EnumMachine",
    "EnumIndex",
    # base
    "BaseEnum",
    "EnumZero",
    "EnumId",
    #
    "EnumView",
    "EnumRepr",
    "EnumStr",
]


from ._enum import EnumId, EnumRepr, EnumStr, EnumZero


class EnumView(EnumStr, EnumRepr):
    """Global Default"""


class BaseEnum(EnumZero, EnumView):
    """Provide Base with Simple View and Modified Access"""


#  LINE: -- frequently used -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PolicyEnum(BaseEnum):  # LATER: Zero? maybe for default?
    """Task and Rule Toggle"""


class EnumMachine(EnumView):  # TODO: sketch StubMachine(Machine)
    """Task Executor"""


class EnumIndex(BaseEnum):  # CHECK: collapse with base??
    """Define the Axis for the {0..N} Members"""


#  LINE: -- boundaries unclear... -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EnumMode(BaseEnum):
    """Task Toggle"""


class EnumOption(BaseEnum):
    """Multiple Selections - Always 1 default (on zero)"""


class PrintOption(EnumOption):
    """(Randomly) toggle views until it looks nice"""


# TODO: ViewOption? ViewEnumCatalog already exists (indirect)


class EnumCatalog(BaseEnum):
    """Foolproof Selection"""


class MixinCatalog(BaseEnum):
    """Select without Surprise"""


#  LINE: -- StateMachine -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class StateGraph(EnumView):
    """Static Decision Tool"""


class Transition(EnumView):
    """Dynamic Decision Tool"""
