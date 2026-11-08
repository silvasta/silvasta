"""
Adapt the SstCoreError to PortLink

- This is intends as the one and only Raiser Implementation in the port
- Still experimental, like the setups outside the port

                                  DependencyLevel.sstcore.port[0.4]
"""


# TASK: 1 single port implementation of Raiser
# - create more universal version
# - improve internal data pipeline
# - maybe keep name: LinkRaiser

__all__: list[str] = [
    "LinkRaiser",
    "LinkRaiserCall",
    #
    "EnumError",
    "FailedDispatchError",
    "FailedHackError",
    #
    "PortLinkError",
    "PortErrorInput",
    "PortErrorSpec",
]


from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Protocol, Unpack

from . import raising
from .raising import Raiser, SstCoreError
from .solid import BaseEnum

#  LINE: -- Error Collection -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#  TODO: integrate into LinkRaiser / PortRaiser


class EnumError(SstCoreError, TypeError):
    """Temporary Resolve the SstEnumMeta blinding"""

    def __init__(
        self, member_or_cls: Enum | type[Enum], /, reason="", *args
    ) -> None:
        """Forward Args to Exception"""
        reason: str = reason or "Failed"
        match BaseEnum.membership(member_or_cls):
            case ():
                who = f"Unknown: {member_or_cls=}"
            case (enum_cls,):
                self.enum: type[BaseEnum] = enum_cls
                who = f"BaseEnum: {enum_cls}"
            case (enum_cls, member):
                self.enum: type[BaseEnum] = enum_cls
                self.member: BaseEnum = member
                who = f"BaseEnum: {enum_cls=}, {member=}"
        super().__init__(f"{who} | {reason=}", *args)


class FailedDispatchError(SstCoreError, NotImplementedError):  # MOVE: ._error?
    # TASK: sync with NotImplementedDispatchError
    """Raise on missing TargetType for singledispatch(method)"""

    def __init__(self, first: Any, *args: Any, **kwargs):
        self.first = first
        msg = f"Missing dispatch target for {type(first).__name__}"
        super().__init__(msg, *(first, *args), **kwargs)


class FailedHackError(SstCoreError):
    """
    It was a nice try, but...

    (I hope I don't have to  explain that this is mostly for internal tests...)
    """

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)


#  LINE: -- Link -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PortLinkError(raising.SstCoreError):
    def __init__(
        self,
        message: str,
        *args,
        text: str | None = None,
        attr: str | None = None,
        source: type | None = None,
        panic: LinkRaiser | None = None,
        **kwargs: Any,
    ):
        self.message: str = message
        self.doc_text: str | None = text
        self.attr: str | None = attr
        self.source: type | None = source
        self.kwargs: dict = kwargs
        self.panic: LinkRaiser = panic or LinkRaiser.Zero
        super().__init__(*args)


class PortErrorInput(raising.ErrorInput, total=False):
    text: str
    attr: str
    source: type


@dataclass(frozen=True)
class PortErrorSpec(raising.ErrorSpec):
    text: str = ""
    attr: str | None = None
    source: type | None = None


class LinkRaiserCall(Protocol):
    def __call__(
        self, *args, **kwargs: Unpack[PortErrorInput]
    ) -> raising.SstCoreError: ...


class LinkRaiser(Raiser):
    Zero = auto()

    MissingPlug = auto()
    PipeLine = auto()
    Inject = auto()
    Reflect = auto()

    __call__: LinkRaiserCall

    @property
    def data(self) -> type[PortErrorSpec]:
        """Override to map to specific raising.ErrorSpec"""
        return PortErrorSpec

    @property
    def custom(self) -> type[PortLinkError]:
        """Override to map to specific Custom Error"""
        return PortLinkError

    @property
    def builtin(self) -> type[Exception] | None:
        """Find Builtin Exception if registered in Raiser"""
        match self:
            case LinkRaiser.Zero:
                return None

            case LinkRaiser.MissingPlug:
                return AttributeError

            case LinkRaiser.PipeLine:
                return RuntimeError

            case LinkRaiser.Inject:
                return AttributeError

            case LinkRaiser.Reflect:
                return AttributeError

    def message(self, data: raising.ErrorSpec) -> str:
        """Override to generate formatted messages based on the Enum state"""

        assert isinstance(data, PortErrorSpec), (
            f"Expected Fieldraising.ErrorSpec, got {type(data)}"
        )
        text: str = data.text or "No __doc__"
        attr: str = data.attr or "Unknown"
        source_name: str = (
            data.source.__name__ if data.source else "Unknown Implementation"
        )

        # TASK: improve!!

        match self:
            case LinkRaiser.Zero:
                return super().message(data)

            case LinkRaiser.MissingPlug:
                return f"Not found: {source_name} for {attr=}"

            case LinkRaiser.PipeLine:
                return f"Issue with: {source_name} for {attr=}"

            case LinkRaiser.Inject:
                return f"Issue for: {source_name}.{attr}, __doc__:{text}"

            case LinkRaiser.Reflect:
                return f"Issue for: {source_name}.{attr}, __doc__:{text}"

        return f"Failed Match: {type(self).__name__}.message: {self=}"
