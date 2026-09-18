"""
Experiment with new Raiser

- The Definition

                                                 DependencyLevel[0]
"""

from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Any,
    NamedTuple,
    Never,
    Protocol,
    TypedDict,
    Unpack,
)

from ...port.attach import DescriptorBase
from ...port.calling import Stringable
from ...port.error import SstCoreError
from ...port.process import NameParsing

type ErrorPair[ErrorT] = SstCoreError | Exception
type Single[ErrorT] = SstCoreError | None


#  LINE: -- DTO and KW -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Reason(Enum):
    """SO FAR UNUSED: another combinatorial approach"""

    Missing = auto()
    Exists = auto()
    Execute = auto()


class ErrorInput[FieldT, UnitT: Any](TypedDict, total=False):
    """Define the Kwarg Space of the Error pipeline"""

    # field: FieldT
    # TODO: make them as well args from here?
    # instance: UnitT | None
    cls_attr_name: str
    #
    owner: type | None
    value: UnitT | Any
    #
    expected: dict
    received: dict


class ErrorData[FieldT, UnitT](NamedTuple):
    """Define the Arg Space of the Internal Pipeline"""

    raiser: str
    #
    field: FieldT
    instance: UnitT | None = None
    cls_attr_name: str = ""  # Cls.attr
    #
    owner: type | None = None
    value: FieldT | Any = None
    #
    expected: tuple[tuple[str, Any], ...] = ()
    received: tuple[tuple[str, Any], ...] = ()
    #
    extra: dict[str, Any] | None = None  # CHECK: can here something change?


class ErrorDTO[ErrorT: Exception](NamedTuple):
    """Define the Boundary of the Outgoing Message"""

    error: type[ErrorT]
    message: str = ""
    args: tuple[Any, ...] = ()

    def __call__(self, *args) -> ErrorT:
        return self.error(self.message, *self.args, *args)

    def fire(self, *args) -> Never:
        raise self(self.message, *self.args, *args)


#  LINE: -- Machinery -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ErrorFormating[ErrorT: SstCoreError](Protocol):
    """Hold templates and fill values"""

    def template(self, reason: Raiser, /) -> str:
        """Store one template for each raising reason"""

    def format(self, keys: dict[str, Stringable]) -> str:
        """Insert keys and get filled pattern"""

    def __call__[FieldT](self, reason: Raiser, /, data: ErrorData) -> str:
        """Process Reason, Field and Data to"""


if TYPE_CHECKING:
    _name: type[ErrorFormating] = NameParsing


class ErrorAssembling[ErrorT: SstCoreError](Protocol):
    """Hold exceptions, mixin builtins and fill values"""

    # IMPORTANT: The Policy!
    # - which args into which exception
    # - how to decide on missing
    # - when choose which builtin or not

    def custom(self, reason: Raiser, /, data: ErrorData) -> ErrorDTO[ErrorT]:
        """Get registred custom Exception that maps to current Raiser"""

    def builtin(self, reason: Raiser, /, data: ErrorData) -> ErrorDTO:
        """Find registred builtin Exception if registred"""

    def compose(self, reason: Raiser, /, data: ErrorData) -> ErrorT:
        """Mix builtin Exception into the custom Error"""

    def __call__(self, reason: Raiser, /, data: ErrorData) -> ErrorDTO[ErrorT]:
        """Collect Format and Compose Exception -> Build DTO"""


# IDEA: Merge ErrorAssembling / ErrorMachine


class ErrorMachine[ErrorT: SstCoreError](Protocol):
    text: ErrorFormating
    error: ErrorAssembling

    def run(self, reason: Raiser, /, data: ErrorData) -> ErrorDTO:
        """Connect Raiser, Assemble and Format to build the Error"""


#  LINE: -- Manager -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class RaiserQuery[ErrorT: SstCoreError](Protocol):
    def __iter__(self) -> tuple[Single[ErrorT] | ErrorPair[ErrorT], ...]:
        """Yield all pairs of Error/Exception"""

    def __contains__(self, target: ErrorT | Exception) -> bool:
        """Is the target Exception already member?"""

    def errors(self) -> tuple[SstCoreError, ...]:
        """Provide all custom Errors, full mapping"""

    def exceptions(self) -> tuple[Exception, ...]:
        """Provide all builtin Exceptions, can be empty"""


class Raiser[ErrorT: SstCoreError](RaiserQuery[ErrorT], Protocol):
    """Core"""

    # TASK: routing, input parsing TypedDict->NamedTuple

    def intact[FieldT: DescriptorBase, UnitT: Any](
        self, field: FieldT, instance: UnitT, **kwargs: Unpack[ErrorInput]
    ) -> ErrorT: ...

    def __call__[FieldT: DescriptorBase, UnitT: Any](
        self, field: FieldT, instance: UnitT, **kwargs: Unpack[ErrorInput]
    ) -> Never:
        """Take all relevant input, process, raise"""
