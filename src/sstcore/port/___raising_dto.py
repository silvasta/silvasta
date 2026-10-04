from collections.abc import Mapping
from typing import Any, Self, TypedDict, Unpack


# Assuming Raiser is defined
class Raiser:
    pass


class ErrorInput(TypedDict, total=False):
    """Define the Kwarg Space of the Error Pipeline"""

    expected: dict[str, Any]
    received: dict[str, Any]
    extra: dict[str, Any]


class BaseErrorData:
    """Shared foundation. No slots or properties to keep it minimal."""

    reason: Raiser
    expected: Mapping[str, Any]
    received: Mapping[str, Any]
    extra: Mapping[str, Any]

    def __init__(
        self,
        reason: Raiser,
        expected: dict[str, Any] | None = None,
        received: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ):
        self.reason = reason
        self.expected = expected or {}
        self.received = received or {}
        self.extra = extra or {}

    @classmethod
    def sanitize(cls, reason: Raiser, **kwargs: Unpack[ErrorInput]) -> Self:
        """Extract the ErrorInput kwargs to form the ErrorData"""
        return cls(
            reason=reason,
            expected=kwargs.get("expected"),
            received=kwargs.get("received"),
            extra=kwargs.get("extra"),
        )


class ErrorData(BaseErrorData):
    """Read-only finalized data (Analogous to PortLinkDocs)"""

    def edit(self) -> MutableErrorData:
        """Spawn a mutable pipeline pre-filled with this data"""
        return MutableErrorData(
            reason=self.reason,
            expected=dict(self.expected),
            received=dict(self.received),
            extra=dict(self.extra),
        )


class MutableErrorData(BaseErrorData):
    """Mutable Error Data pipeline (Analogous to PortLinks)"""

    expected: dict[str, Any]
    received: dict[str, Any]
    extra: dict[str, Any]

    def save(self) -> ErrorData:
        """Freeze into read-only ErrorData"""
        return ErrorData(
            reason=self.reason,
            expected=self.expected,
            received=self.received,
            extra=self.extra,
        )


x = ErrorData.sanitize(Raiser())
y = x.edit()

y = MutableErrorData.sanitize(Raiser())
