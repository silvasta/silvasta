"""
Adapt the SstError to PortLink

- This is intends as the one and only Raiser Implementation in the port
- Still experimental, like the setups outside the port

                                  DependencyLevel.sstcore.port[0.4]
"""
# NEXT: decide on setup on next update

__all__: list[str] = [
    "LinkRaiser",
    "LinkRaiserCall",
    #
    "PortLinkError",
    "PortErrorInput",
    "PortErrorSpec",
]


from enum import auto
from typing import Any, Protocol, Unpack

from .. import raising
from ..raising import Raiser, RaiserMeta


class PortLinkError(raising.SstPortError):
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


#  LINE: -- Raiser with Immutable Cls -- -- - -- -- - -- -- - -- -- - -- -- - -- --

# NEXT: decide on setup on next update


class PortLinkRaiser(metaclass=RaiserMeta):
    """Fast V2 Raiser for port.link operations."""

    # FIX: breaks NameParser
    # missing_plug = RaiserField[[type, str]](
    #     AttributeError, "Not found: {0} for attr={1!r}"
    # )
    # pipeline = RaiserField[[type, str]](
    #     RuntimeError, "Pipeline issue with {0} for attr={1!r}"
    # )
    # inject = RaiserField[[type, str, str]](
    #     AttributeError, "Inject issue for {0}.{1}, __doc__={2!r}"
    # )
    # reflect = RaiserField[[type, str, str]](
    #     AttributeError, "Reflect issue for {0}.{1}, __doc__={2!r}"
    # )


#  LINE: -- Raiser with Enum Setup -- -- - -- -- - -- -- - -- -- - -- -- - -- --

# NEXT: decide on setup on next update


class PortErrorInput(raising.ErrorInput, total=False):
    text: str
    attr: str
    source: type


class PortErrorSpec(raising.ErrorSpec):
    text: str = ""
    attr: str | None = None
    source: type | None = None


class LinkRaiserCall(Protocol):
    def __call__(
        self, *args, **kwargs: Unpack[PortErrorInput]
    ) -> raising.SstError: ...


# NEXT: decide on setup on next update
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
