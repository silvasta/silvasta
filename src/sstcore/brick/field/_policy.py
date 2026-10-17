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
from ..none import UNSET
from ._base import ReadField
from ._extend import TypedField


class PolicyFieldEngine[EnumT: PolicyEnum](TypedField[EnumT]):
    """Implement Policy and Execution Logic"""

    enum_type: type[EnumT]

    def __init__(
        self,
        policy: type[EnumT] | EnumT,
        /,
        *args,
        default: PolicyEnum | UNSET = UNSET,
        **kwargs,
    ):
        match PolicyEnum.membership(policy):
            case ():
                raise self.raiser.Validation(
                    self,
                    text="Derive from PolicyEnum!",
                    expected={"policy": PolicyEnum},
                    received={"policy": policy},
                )
            case (enum_cls,):
                self.enum_type: type[EnumT] = enum_cls
                _extracted_default = self.enum_type.resolve(0, default=UNSET)

            case (enum_cls, enum_unit):
                self.enum_type: type[EnumT] = enum_cls
                _extracted_default = enum_unit

        if default is UNSET and _extracted_default is not UNSET:
            default: EnumT = _extracted_default  # UnboundError impossible?

        super().__init__(
            *args, types=self.enum_type, default=default, **kwargs
        )

    def validate(self, unit: object, value: EnumId[EnumT]) -> EnumT:
        resolved_value: EnumT = self.enum_type.resolve(value)
        return super().validate(unit, resolved_value)


@portlink(attach.PolicyDescriptor)
class PolicyField[EnumT: PolicyEnum](PolicyFieldEngine[EnumT], ReadField):
    """PolicyEngine with Simple ReadField"""


class PolicyMatchMixin[FieldT, EnumT: PolicyEnum](ReadField[FieldT]):
    """Extend the Policy Read Pipeline"""

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

    def match(self, unit: object, *args, **kwargs):
        if self._match is None or not self.active:
            raise self.raiser.Function(self, unit)
        _current_policy = self.read(unit)
        return self._match(_current_policy, unit, *args, **kwargs)


@portlink(attach.PolicyDescriptor)
class MatchPolicyField[EnumT: PolicyEnum](PolicyFieldEngine, PolicyMatchMixin):
    """PolicyEngine with intercepting Enum Match Function"""
