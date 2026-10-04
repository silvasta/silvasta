"""
Define the Shape and Behaviour of the Solid Objects

- Collect ideas for Concepts and possible Bases

                                    DependencyLevel.sstcore.port[1]
"""

__all__: list[str] = [
    "PolicyEnum",
    "EnumMachine",
    "EnumId",
    "EnumIndex",
    # base
    "BaseEnum",
    "EnumZero",
    "EnumRepr",
    "EnumStr",
]


from ._enum import EnumRepr, EnumStr, EnumZero


class EnumView(EnumStr, EnumRepr): ...


class BaseEnum(EnumZero, EnumView):
    """Provide Base with Simple View and Modified Access"""


#  LINE: -- frequently used -- -- - -- -- - -- -- - -- -- - -- -- - -- --

type EnumId[EnumT] = EnumT | str | int


class EnumIndex(BaseEnum):
    """Define the Axis for the {0..N} Members"""


class EnumMachine(EnumView):  # TODO: sketch StubMachine(Machine)
    """Task Executor"""


class PolicyEnum(BaseEnum):  # TODO: attach to PolicyDescriptor
    """Task Toggle"""


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
