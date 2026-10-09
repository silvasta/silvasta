"""
Define the Shape and Behaviour of the Solid Objects

- Collect ideas for Concepts and possible Bases

                                    DependencyLevel.sstcore.port[1]
"""

__all__: list[str] = [
    # common
    "PolicyEnum",
    "EnumMachine",
    # base
    "BaseEnum",
    "EnumId",
    "EnumRelation",
    #
    "EnumView",
    "EnumRepr",
    "EnumStr",
]


from ._enum import EnumId, EnumRelation, EnumRepr, EnumStr, SstEnumMeta


class EnumView(EnumStr, EnumRepr):
    """Global Default"""


class BaseEnum(EnumView, metaclass=SstEnumMeta):
    """Provide Base with Simple View and Modified Access"""


class EnumZero(BaseEnum, zero=True):
    """Index based Enum - activate (permanentely) with walk=True"""


#  LINE: -- frequently used -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PolicyEnum(EnumZero, walk=True):
    """Task and Rule Toggle"""

    def __bool__(self):  # CHECK: maybe for option? or for policy?
        """Default Policy mapped to Index 0"""
        return self.value == 0


class EnumMachine(BaseEnum):  # TODO: sketch StubMachine(Machine)
    """Task Executor"""


#  LINE: -- boundaries unclear... -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EnumMode(BaseEnum, walk=True):  # CHECK: same as Option?
    """Task Toggle"""


# IDEA: Mode:= no zero, Option:= zero as default
# - if so, mount MRO walk to meta for detecting superclasses with flag


class EnumOption(EnumZero):
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
