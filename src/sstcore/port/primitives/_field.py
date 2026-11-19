"""
Adapt the SstError to PortLink

- This is intends as the one and only Raiser Implementation in the port
- Still experimental, like the setups outside the port

                                  DependencyLevel.sstcore.port[0.X]
"""

__all__: list[str] = [
    "TupleField",
]

from collections.abc import Callable, Hashable
from typing import Any, Self, overload

from ..empty import VOID, MayBe, MayNot


class TupleField[Value]:  # RENAME: at second usage!
    """
    Descriptor on Immutable Object

    Assign WithOut type hint, like:
      - sep = TupleField[str]("=")
      - otherwise the Field is included in the Tuple!

    """

    def __init__(self, default: MayBe[Value]):
        self._default: MayBe[Value] = default
        self._values: dict[Hashable, Value] = {}

    def __set_name__(self, host: type, name: str) -> None:
        """Define the Name, Assigner:{initial owner} and Hoster:{last owner}"""
        self._name: str = name
        self._host: type = host
        # NEXT: find best naming
        self._caller: type = host

    def __call__[Fn: Callable](self, func: Fn) -> Fn:
        """Make a Method Exchangeable"""
        self._default: Fn = func
        return func

    def __str__(self):
        """Represent (HostCls::)Cls.field_name"""
        return f"{self._scope}.{self._name}"

    def __repr__(self):
        """Represent the Field, Owner(s) and show the Cache"""
        return f"{type(self).__name__}::{self}[{self._values=}]"

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
        """Access the cache by generated Key or set Default"""
        self._caller = caller
        if unit is None:
            return self
        if unit not in self:
            self[unit] = self._default
        return self[unit]

    def __set__(self, unit: Any, value: Value) -> None:
        """Update the per Instance Cache with the Value"""
        self[unit] = value

    def __contains__(self, unit: Any):
        return self._id(unit) in self._values

    def __getitem__(self, unit: Any):
        return self._values[self._id(unit)]

    def __setitem__(self, unit: Any, value: Any):
        if value is VOID:
            raise RuntimeError(f"Assign Value or Default to Access: {self}")
        self._values[self._id(unit)] = value

    def __delete__(self, unit: Any) -> None:
        """Remove the Value of Unit from the Cache"""
        self._values.pop(self._id(unit), None)

    # TASK: improve _id management and cache delete

    def _id(self, unit: Any, /) -> Hashable:
        """Subhook: Hopefully randomized enough"""
        return id(self), id(unit), id(type(unit))
