"""
Adapt the SstCoreError to PortLink

                                                 DependencyLevel[X]
"""

from dataclasses import dataclass
from enum import auto
from typing import Any, Never, Protocol, Unpack

from ..raising import (
    ErrorData,
    ErrorInput,
    ErrorMachine,
    ErrorOutput,
    Raiser,
    SstCoreError,
)


class PortErrorInput(ErrorInput, total=False):
    text: str
    attr: str
    source: type


class LinkRaiserCall(Protocol):
    def __call__(
        self, *args, **kwargs: Unpack[PortErrorInput]
    ) -> Exception: ...


@dataclass(frozen=True)
class PortErrorData(ErrorData):
    reason: LinkRaiser
    text: str | None = None
    attr: str | None = None
    source: type | None = None


class ErrorBuilder(ErrorMachine):
    @classmethod
    def custom(cls, data: ErrorData) -> type[SstCoreError]:
        """Get Custom Exception registred in Raiser"""
        if data.reason == LinkRaiser.RAW:
            return SstCoreError
        return PortLinkError

    @classmethod
    def builtin(cls, data: ErrorData) -> type[Exception] | None:
        """Find Builtin Exception if registred in Raiser"""
        match data.reason:
            case LinkRaiser.RAW:
                ...
            case LinkRaiser.MissingPlug:
                return AttributeError

            case LinkRaiser.PipeLine:
                return RuntimeError

            case LinkRaiser.Inject:
                return AttributeError

            case LinkRaiser.Reflect:
                return AttributeError

    @classmethod
    def message(cls, data: ErrorData) -> str:
        """Find Builtin Exception if registred in Raiser"""
        return f"Error in Port!! ... {data.reason}"


class LinkRaiser(Raiser):
    RAW = auto()

    MissingPlug = auto()
    PipeLine = auto()
    Inject = auto()
    Reflect = auto()

    __call__: LinkRaiserCall

    def order(self, data: ErrorData) -> ErrorOutput:
        return ErrorBuilder.run(data)


class PortLinkError(SstCoreError):
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


def how_to_use1() -> ErrorData:
    return LinkRaiser.RAW.sanitize()


def how_to_use2() -> ErrorOutput:
    return LinkRaiser.PipeLine.dto()


def how_to_use3() -> Never:
    assembled: Exception = LinkRaiser.PipeLine(None, "build", Raiser)
    raise assembled


def how_to_use4() -> Never:
    LinkRaiser.Inject.dto().fire()
