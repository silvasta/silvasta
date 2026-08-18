"""
Functor - Define the Shape of Functions as Objects as Functions

Base:
- Functorial: Define the Core functionality
- SafeFunctorial: Control Errors with Handlers
  - ErrorPolicy: Decide the default behaviour

Extended: (TODO)
- EmitFunctorial: Report the Status
- DecoFunctorial: Act on Signatures

"""

from collections.abc import Callable
from enum import StrEnum
from typing import Concatenate, Protocol


class Functorial[**Param, Result](Protocol):
    """Combine values and functions to advanced executables"""

    @property
    def name(self) -> str: ...
    @property
    def emit(self, *args, **kwargs) -> None: ...

    def __call__(self, *args: Param.args, **kwargs: Param.kwargs) -> Result:
        """The Core of the entire Topic, override or inject _func"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Essentials
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class SafeFunctorial[**Param, Result](Protocol):
    """Provide safe execution environement"""

    # TEST: still congruent?

    catch: Callable[Concatenate[Exception, Param], Result | None] | None

    def safe(self, *args: Param.args, **kwargs: Param.kwargs) -> Result | None:
        """Catch and handle"""

    @property
    def error_policy(self) -> ErrorPolicy: ...
    @property
    def exit_code(self) -> int: ...


class ErrorPolicy(StrEnum):
    LOG_AND_CONTINUE = "log"
    LOG_AND_EXIT = "exit"
    RE_RAISE = "raise"


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Extensions
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class DecoFunctorial[**P, R](Protocol):
    """Execute on top of other functions"""
