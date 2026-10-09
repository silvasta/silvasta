"""
Adapt the SstCoreError to PortLink

- This is intendes as the one and only Raiser Implementation in the port
- Still experimental, like the setups outside the port

                                                 DependencyLevel[3]
"""

# TASK: 1 single port implementation of Raiser
# - create more universal version
# - imporve internal data pipeline
# - maybe keep name: LinkRaiser

__all__: list[str] = [
    "LinkRaiserCall",
    "PortErrorInput",
    "PortErrorData",
    "LinkRaiser",
    "PortLinkError",
]


from dataclasses import dataclass
from enum import auto
from typing import Any, Protocol, Unpack

from . import raising
from .raising import Raiser


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
        self.panic: LinkRaiser = panic or LinkRaiser.RAW
        super().__init__(*args)


class PortErrorInput(raising.ErrorInput, total=False):
    text: str
    attr: str
    source: type


@dataclass(frozen=True)
class PortErrorData(raising.ErrorData):
    text: str | None = None
    attr: str | None = None
    source: type | None = None
    # IDEA: port,plug == Protocol,Cls


class LinkRaiser(Raiser):
    RAW = auto()

    MissingPlug = auto()
    PipeLine = auto()
    Inject = auto()
    Reflect = auto()

    __call__: LinkRaiserCall

    @property
    def data(self) -> type[PortErrorData]:
        """Override to map to specific raising.ErrorData"""
        return PortErrorData

    @property
    def custom(self) -> type[PortLinkError]:
        """Override to map to specific Custom Error"""
        return PortLinkError

    @property
    def builtin(self) -> type[Exception] | None:
        """Find Builtin Exception if registred in Raiser"""
        match self:
            case LinkRaiser.RAW:
                return None

            case LinkRaiser.MissingPlug:
                return AttributeError

            case LinkRaiser.PipeLine:
                return RuntimeError

            case LinkRaiser.Inject:
                return AttributeError

            case LinkRaiser.Reflect:
                return AttributeError

    def message(self, data: raising.ErrorData) -> str:
        """Override to generate formatted messages based on the Enum state"""

        assert isinstance(data, PortErrorData), (
            f"Expected Fieldraising.ErrorData, got {type(data)}"
        )
        text: str = data.text or "No __doc__"
        attr: str = data.attr or "Unknown"
        source_name: str = (
            data.source.__name__ if data.source else "Unknown Implementation"
        )

        # TASK: improve!!

        match self:
            case LinkRaiser.RAW:
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


class LinkRaiserCall(Protocol):  # TASK: think about parametrization
    def __call__(
        self, *args, **kwargs: Unpack[PortErrorInput]
    ) -> raising.SstCoreError: ...
