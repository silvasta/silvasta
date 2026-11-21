"""
Adapt the SstError to PortLink

- This is intends as the one and only Raiser Implementation in the port
- Still experimental, like the setups outside the port

                                  DependencyLevel.sstcore.port[0.X]
"""

__all__: list[str] = [
    "TupleField",
]

from collections.abc import Callable
from typing import Any, Self, overload

from ..empty import VOID, MayBe, MayNot


class TupleField[Value]:  # CHECK: Tuple?
    """
    Generate Non-Member Field for (Named)Tuple with mutable values

    Assign WITHOUT type hint, like:
      - sep = TupleField[str]("=")
      - otherwise the Field is included as tuple member!

    """

    def __init__(self, default: MayBe[Value], /):
        self._default: MayBe[Value] = default

    def __set_name__(self, host: type, name: str) -> None:
        """Define the Name, Assigner:{initial owner} and Hoster:{last owner}"""
        self._name: str = name
        self._host: type = host
        self._caller: type = host

    def __call__[Fn: Callable](self, func: Fn) -> Fn:
        """Make a Method Exchangeable"""
        self._default: Fn = func
        return func

    def __str__(self):
        """Represent (HostCls::)Cls.field_name"""
        return f"{self._scope}.{self._name}"

    @property
    def _scope(self) -> str:
        """Represent Host or Host::Caller"""
        _maybe_caller = f"::{self._caller.__name__}" if self._inherited else ""
        return f"{self._host.__name__}{_maybe_caller}"

    @property
    def _inherited(self) -> bool:
        """Was the field last accessed through a subclass rather than its host?"""
        return self._host is not self._caller

    @overload
    def __get__(self, unit: None, caller: type) -> Self: ...
    @overload
    def __get__(self, unit: Any, caller: type) -> Value: ...

    def __get__(self, unit: MayNot, caller: type) -> Self | Value:
        """Extract per Unit from Cache or try set Default"""
        # TEST: differences in the ids
        # print(f"Get: {self}")
        # print(f"{self._host=}\n{self._caller=}\n{self._inherited=}")
        # print(f"{id(self._host)=}\n{id(self._caller)=}\n{id(self._inherited)=}")
        self._caller = caller  # TODO: where to place this??
        return self if unit is None else self[unit]

    def __set__(self, unit: Any, value: Value) -> None:
        """Update the per Instance Cache with the Value"""
        self[unit] = value

    def __getitem__(self, unit: Any):
        if unit not in self:
            self[unit] = self._default
        return vars(unit)[self._name]

    def __setitem__(self, unit: Any, value: Any):
        if value is VOID:
            raise RuntimeError(f"Assign Value or Default to Access: {self}")
        vars(unit)[self._name] = value

    def __contains__(self, unit: Any):
        """Heavily Wired! Change with care..."""
        return self._name in vars(unit)

    def __delete__(self, unit: Any) -> None:
        """Remove the Value of Unit from the Cache"""
        vars(unit).pop(self._name, None)
