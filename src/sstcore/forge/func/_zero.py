"""
View Assembly

- Don't use from ..view as Functor might export there

"""

__all__: list[str] = [
    "FunctorMetaInput",
    #
    "BaseParamSpec",
    "DataClassSpec",
    #
    "FunctorView",
]

from dataclasses import dataclass, fields
from typing import Any, Self, TypedDict, dataclass_transform

from ...brick import reflect
from ...brick.color import colorize
from ...brick.color.box import Colors
from ...brick.format import norm
from ...port.color import Color
from ...port.represent import Richable
from ..engine import FunctorMetaData

colors = Colors()

FunctorMetaInput = FunctorMetaData(color=Color.GREEN)


@dataclass_transform(kw_only_default=True)
class BaseParamSpec:  # TODO: compare with EventDTO::ParamSpec, find global base
    """Setup Base for Input sanitizing DataClasses"""

    def __init_subclass__(cls, kw_only: bool = True, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        dataclass(kw_only=kw_only, **kwargs)(cls)


class BaseInput(TypedDict, total=False): ...


class DataClassSpec(BaseParamSpec):
    """Define Defaults for Input and Sanitize"""

    @classmethod  # IDEA: combine with @castarg?
    def absorb(cls, kwargs) -> Self:
        """Build Spec with input from kwargs (extracted and destroyed)"""
        return cls(
            **{
                field.name: kwargs.pop(field.name)
                for field in fields(class_or_instance=cls)
                if field.name in kwargs
            }
        )


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# # in forge.func._safe
# class SafeFunctorSpec[**A, R](DataClassSpec):
#     catch: Catch[A, R] | None = None
#     policy: ErrorPolicy | None = None
#     exit_code: int | None = None
#
#
# @portlink(SafeFunctorial)
# class SafeFunctor[**Args, Result](BaseFunctor[Args, Result]):
#     policy: PolicyField[ErrorPolicy] = PolicyField(ErrorPolicy.LOG_AND_CONTINUE)
#     exit_code: RequiredField[int] = RequiredField(types=int, default=1)
#
#     def __init__(self, **kwargs: Unpack[SafeFunctorInput[Args, Result]]):
#         # Pops only `catch`, `policy`, `exit_code` and leaves `call`, `name` for super()
#         _spec = SafeFunctorSpec.absorb(kwargs)
#
#         if _spec.catch is not None:
#             self._catch: Catch[Args, Result] = _spec.catch
#         if _spec.policy is not None:
#             self.policy = _spec.policy
#         if _spec.exit_code is not None:
#             self.exit_code = _spec.exit_code
#
#         super().__init__(**kwargs)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class FunctorView:
    _data: FunctorMetaData

    def __str__(self) -> str:
        return f"[({reflect.clsname(self)})][{reflect.name(self)}]"

    def __repr__(self) -> str:
        return f"{self}({norm.dict_to_str(vars(self))})"

    #  LINE: -- Select, later on -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __rich__(self) -> str:
        return f"{reflect.clsname(self)}[{reflect.name(self)}]"

    def __rich1__(self) -> Richable:
        return colors(reflect.clsname(self), self._data.color)

    def __rich2__(self) -> Richable:
        return colorize.modules(self)
