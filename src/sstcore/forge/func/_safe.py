"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

__all__: list[str] = [
    "SafeFunctor",
]


import sys
from collections.abc import Callable
from typing import Concatenate, NoReturn

from ...brick.field import PolicyField, RequiredField
from ...brick.field._strategy import strategy
from ...port import functorial
from ...port.functorial import ErrorPolicy
from ...port.link import portlink
from ._tor import BaseFunctor

type _Catch[**A, R] = Callable[Concatenate[Exception, A], R | None]


@portlink(functorial.SafeFunctorial)
class SafeFunctor[**Args, Result](BaseFunctor[Args, Result]):
    """Protect the Execution, Hanldle Errors, everything able to customize"""

    policy = PolicyField(ErrorPolicy.LOG_AND_CONTINUE)
    exit_code = RequiredField(types=int, default=1)

    def __init__(self, catch: _Catch[Args, Result] | None = None, **kwargs):
        if catch is not None:
            # CHECK: if direct assing works at usage!
            # needed because of confusion below
            setattr(self, "catch", catch)  # noqa:B010
        super().__init__(**kwargs)

    def safe(
        self, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | None | NoReturn:
        try:
            return self(*args, **kwargs)
        except Exception as error:
            self.catch(error, *args, **kwargs)

    @strategy
    def catch(
        self, error: Exception, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | None | NoReturn:
        """Execute pure Policy if catch is not defined"""
        self.emit(
            f"{self} failed: {error}", level="CRITICAL", param=(args, kwargs)
        )
        match self.policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise error
