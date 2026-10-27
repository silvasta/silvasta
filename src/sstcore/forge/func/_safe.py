"""
Implement the Functors for calltions and more

- Pick and provide the best of OOP/FP

"""

__all__: list[str] = [
    "SafeFunctor",
]


import sys
from typing import NoReturn, Unpack

from ...brick.field import PolicyField, RequiredField
from ...brick.field._strategy import StrategyField
from ...port.empty import VOID
from ...port.functorial import Catch, ErrorPolicy, SafeFunctorial
from ...port.link import portlink
from ._tor import BaseFunctor, FunctorInput
from ._zero import DataClassSpec


class SafeFunctorInput[**A, R](FunctorInput, total=False):
    catch: Catch[A, R]
    policy: ErrorPolicy
    exit_code: int


class SafeFunctorSpec[**A, R](DataClassSpec):
    catch: Catch[A, R] | None = None
    policy: ErrorPolicy | None = None
    exit_code: int | None = None


@portlink(SafeFunctorial)
class SafeFunctor[**Args, Result](BaseFunctor[Args, Result]):
    """Protect the Execution, Handle Errors, everything able to customize"""

    policy: PolicyField[ErrorPolicy] = PolicyField(ErrorPolicy.LOG_AND_CONTINUE)
    exit_code: RequiredField[int] = RequiredField(types=int, default=1)

    def __init__(self, **kwargs: Unpack[SafeFunctorInput[Args, Result]]):
        _spec = SafeFunctorSpec.absorb(kwargs)

        if _spec.catch is not None:
            self._catch: Catch[Args, Result] = _spec.catch
        if _spec.policy is not None:
            self.policy: ErrorPolicy = _spec.policy
        if _spec.exit_code is not None:
            self.exit_code: int = _spec.exit_code

        super().__init__(**kwargs)

    @StrategyField(bind_to_self=True)
    def _catch(
        self, error: Exception, /, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | VOID | NoReturn:
        """Execute pure Policy if catch is not defined"""
        self._emit(  # LATER: pack this into Raiser
            f"{self} failed: {error}", level="CRITICAL", param=(args, kwargs)
        )
        match self.policy:
            case ErrorPolicy.LOG_AND_CONTINUE:
                return VOID

            case ErrorPolicy.LOG_AND_EXIT:
                sys.exit(self.exit_code)

            case ErrorPolicy.RE_RAISE:
                raise error
        raise error  # type checker fix, replace later on

    def raw(self, *args: Args.args, **kwargs: Args.kwargs) -> Result:
        """Execute the unsafed raw Functor __call__"""
        return super().__call__(*args, **kwargs)

    def safe(
        self, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | NoReturn | VOID:
        """Fallback to custom catch logic on Fail"""
        try:
            return self.raw(*args, **kwargs)
        except Exception as error:
            return self._catch(error, *args, **kwargs)

    def __call__(
        self, *args: Args.args, **kwargs: Args.kwargs
    ) -> Result | NoReturn:
        """Wire __call__ in Safe mode Iff _catch returns LSP-Conform result"""
        if (result := self.safe(*args, **kwargs)) is not VOID:
            return result
        self._emit(  # LATER: pack this into Raiser, consider original error
            f"{self}[{self.policy}] Violation of __call__: VOID is not allowed!"
        )
        raise TypeError("Invalid __call__", {"functor": self, "result": result})
