"""
Provide the Bricks for Descriptor Compositions

- Govern Policy and Execution
                                                 DependencyLevel[2]
"""

__all__: list[str] = [
    "PolicyField",
    "MatchPolicyField",
    #
    "PolicyFieldEngine",
    "PolicyMatchMixin",
]

from collections.abc import Callable

from ...port import attach
from ...port.link import portlink
from ...port.solid import EnumId, PolicyEnum
from ._base import ReadField
from ._extend import TypedField


class PolicyFieldEngine[EnumT: PolicyEnum](TypedField[EnumT]):
    """Implement Policy and Execution Logic"""

    def __init__(
        self, enum: type[EnumT], /, *args, frozen: bool = False, **kwargs
    ):
        self.enum: type[EnumT] = enum
        self.frozen: bool = frozen  # MOVE: FrozenFieldMixin?
        super().__init__(*args, types=enum, **kwargs)

    def validate(self, unit: object, value: EnumId[EnumT]) -> EnumT:
        if self.frozen and self._has_val(unit):  # MOVE: FrozenFieldMixin?
            raise self.raiser.ReadOnly(self, unit)

        value: EnumT = self.enum_type.resolve(value)  # ty:ignore
        return super().validate(unit, value)


@portlink(attach.PolicyDescriptor)
class PolicyField[EnumT: PolicyEnum](PolicyFieldEngine[EnumT], ReadField):
    """PolicyEngine with Simple ReadField"""


class PolicyMatchMixin[FieldT, EnumT: PolicyEnum](ReadField[FieldT]):
    """Extend the Policy Read Pipelin"""

    enum_type: EnumT

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
            raise self.raiser.ReadMissing(self, unit)
        return self._get_val(unit)

    def match(self, unit: object, *args, **kwargs):
        if self._match is None or not self.active:
            raise self.raiser.Function(self, unit)
        _current_policy = self.read(unit)
        return self._match(_current_policy, unit, *args, **kwargs)


@portlink(attach.PolicyDescriptor)
class MatchPolicyField[EnumT: PolicyEnum](PolicyFieldEngine, PolicyMatchMixin):
    """PolicyEngine with intercepting Enum Match Function"""
