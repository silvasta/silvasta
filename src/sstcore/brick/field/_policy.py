"""
Provide the Bricks for Descriptor Compositions

- Govern Policy and Execution
                                                 DependencyLevel[2]
"""

__all__: list[str] = [
    "PolicyField",
    "MatchPolicyField",
]

from collections.abc import Callable
from typing import TYPE_CHECKING

from ...port import attach
from ...port.govern import EnumId, PolicyEnum
from ._base import ReadField
from ._extend import TypedField

# INFO: type EnumId[EnumT] = EnumT | str | int
# CHECK: for typing: type Identifier = EnumId[PolicyEnum]


class PolicyFieldEngine[EnumT: PolicyEnum](TypedField[EnumT]):
    """Implement Policy and Execution Logic"""

    def __init__(
        self,
        enum_type: type[EnumT],
        *args,
        frozen: bool = False,
        **kwargs,
    ):
        self.enum_type: type[EnumT] = enum_type
        self.frozen: bool = frozen  # MOVE: FrozenFieldMixin?
        super().__init__(*args, **kwargs)

    def validate(self, unit: object, value: EnumId[EnumT]) -> EnumT:
        if self.frozen and self._has_val(unit):  # MOVE: FrozenFieldMixin?
            raise self.on_error.ReadOnly(self, unit)()

        value: EnumT = self.enum_type.resolve(value)  # ty:ignore
        return super().validate(unit, value)


class PolicyMatchMixin[FieldT, EnumT: PolicyEnum](ReadField[FieldT]):
    """Extend the Policy Read Pipelin"""

    enum_type: EnumT

    # LATER: specify:enum_match: Callable
    def __init__(
        self,
        *args,
        enum_match: Callable | None = None,
        active: bool = True,
        **kwargs,
    ):
        self._match: Callable | None = enum_match
        self.active: bool = active
        super().__init__(*args, **kwargs)

    def read(self, unit: object) -> FieldT:
        if not self._has_val(unit):
            raise self.on_error.ReadMissing(self, unit)()
        return self._get_val(unit)

    def match(self, unit: object, *args, **kwargs):
        if self._match is None or not self.active:
            raise self.on_error.Function(self, unit)()
        _current_policy = self.read(unit)
        return self._match(_current_policy, unit, *args, **kwargs)


# IMPORTANT: the manual
# class BaseVault[Item, Vault: Vaults, U, A: Any]:
#     # Set default to a specific Enum member, not the class
#     on_conflict = MatchPolicyField(
#         VaultPolicy,
#         default=VaultPolicy.RAISE,
#         enum_match=default_conflict_handler)
#     def add(self, data: Item) -> Vault:
#         if self._is_conflict(data):
#             # Access the descriptor from the class to call match()
#             return type(self).on_conflict.match(unit=self, data=data)
#         # ... normal add logic ...


class PolicyField[EnumT: PolicyEnum](PolicyFieldEngine[EnumT], ReadField):
    """PolicyEngine with Simple ReadField"""


class MatchPolicyField[EnumT: PolicyEnum](PolicyFieldEngine, PolicyMatchMixin):
    """PolicyEngine with intercepting Enum Match Function"""


if TYPE_CHECKING:
    _policy: type[attach.PolicyDescriptor] = PolicyField
    _policy: type[attach.PolicyDescriptor] = MatchPolicyField
