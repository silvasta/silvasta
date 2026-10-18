"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

__all__: list[str] = [
    "SafeFunctor",
]


import sys
from typing import NoReturn

from ...brick.field import PolicyField, RequiredField
from ...brick.field._strategy import StrategyField
from ...port.functorial import Catch, ErrorPolicy, SafeFunctorial
from ...port.link import portlink
from ._tor import BaseFunctor, FunctorInput


@portlink(SafeFunctorial)
class SafeFunctor[**Args, Result](
    BaseFunctor[Args, Result],
    data=FunctorInput,  # TODO: handle by Base!
):
    """Protect the Execution, Handle Errors, everything able to customize"""

    policy = PolicyField(ErrorPolicy.LOG_AND_CONTINUE)
    exit_code: RequiredField[int] = RequiredField(types=int, default=1)

    def __init__(self, catch: Catch[Args, Result] | None = None, **kwargs):
        if catch is not None:
            self._catch: Catch[Args, Result] = catch
        super().__init__(**kwargs)

    def safe(
        self, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | None | NoReturn:
        try:
            return self(*args, **kwargs)
        except Exception as error:
            return self._catch(error, *args, **kwargs)

    @StrategyField(bind_to_self=True)
    def _catch(
        self, error: Exception, /, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | None | NoReturn:
        """Execute pure Policy if catch is not defined"""
        self._emit(
            f"{self} failed: {error}", level="CRITICAL", param=(args, kwargs)
        )
        match self.policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return None

            case ErrorPolicy.LOG_AND_EXIT:
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise error
