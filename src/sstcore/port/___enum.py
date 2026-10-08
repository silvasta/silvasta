"""
Govern the Shape and Structure of the Strict and Reliable Container

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "SstEnumMeta",
    "EnumRelation",
    "EnumId",
    # view
    "EnumStr",
    "EnumRepr",
    #
    "EnumStr1",
    "EnumStr2",
    "EnumRepr1",
    "EnumRepr2",
]


from enum import Enum, EnumMeta

type EnumId[EnumT: Enum] = EnumT | str | int


type EnumRelation[T: Enum] = tuple[type[T], T] | tuple[type[T]] | tuple[()]


class SstEnumMeta(EnumMeta):
    """
    Set Count to Zero

    MEMBER = auto()

    - Self.name = MEMBER
    - Self.value = auto() = 0,..,N
        - len(Self) = N

    Ideas:
    - __bool__: for Options
    - index: -> int
    - key: -> str, similar to name
    - short: for LOG_AND_CONTINUE  -> "log", maybe as key?

    """  # LATER:  better description

    _is_zero_indexed: bool = False
    _walk_for_zero: bool = False

    @classmethod
    def __prepare__(_mcls, cls, bases, **kwargs):  # noqa:N804

        enum_dict = super().__prepare__(cls, bases, **kwargs)

        # AI: new approach, superclass can define walk=True,
        # -> that must hold for subclasses as well
        # cases:
        # - zero True on parent, walk True on parent, child always zero except on override
        # - zero True on parent, walk False on parent, child can override either
        # - zero False on parent, walk True on parent, child must override zero
        # - zero False on parent, walk False on parent, child must override zero
        # walk=True works as always inherited attribute while zero must be set explicitly or be included by walk
        # - is this reasonable? goal is to allow inherited zero with walk but default to enforced override

        _use_zero = kwargs.get("zero", False)
        if not _use_zero:
            _walk_for_zero = kwargs.get("walk", False)
            if not _walk_for_zero:
                _walk_for_zero = any(
                    getattr(b, "_walk_for_zero", False) for b in bases
                )
            if _walk_for_zero:
                _use_zero = any(
                    getattr(b, "_is_zero_indexed", False) for b in bases
                )
        if _use_zero:
            enum_dict["_generate_next_value_"] = staticmethod(from_zero)
        # AI: END: new approach

        # AI: version before
        if (_direct_zero := kwargs.get("zero", False)) or (
            (_walk_for_zero := kwargs.get("walk", False))
            and any(getattr(b, "_is_zero_indexed", False) for b in bases)
        ):
            enum_dict["_generate_next_value_"] = staticmethod(from_zero)
        # AI: END: version before

        return enum_dict

    def __new__(metacls, cls, bases, classdict, **kwargs):
        """Destroy all custom kwargs and attach Zero"""

        _is_zero: bool = kwargs.pop("zero", False)
        _walk_for_zero: bool = kwargs.pop("walk", False)

        new_enum_cls = super().__new__(
            metacls, cls, bases, classdict, **kwargs
        )

        new_enum_cls._is_zero_indexed = _is_zero
        new_enum_cls._walk_for_zero = _walk_for_zero

        return new_enum_cls

    def membership(cls, target, /) -> EnumRelation:
        """Check if target is Enum class or instance"""

        if isinstance(target, cls):
            return (type(target), target)

        if isinstance(target, EnumMeta) and issubclass(target, cls):
            return (target,)

        return ()

    def resolve(cls, identifier: EnumId, /, default=None):
        """Map [int|str|EnumT] to BaseEnum derivative, default or Raise"""
        try:
            match identifier:
                case cls():
                    return identifier

                case int() as index:
                    return cls(index)

                case str() as name:
                    for member_name, member in cls._member_map_.items():
                        if name.lower() == member_name.lower():
                            return member
                    raise KeyError(f"Unrecognized name: {identifier!r}")
                case _:
                    raise TypeError(f"Unrecognized type: {identifier!r}")

        except (ValueError, KeyError, TypeError) as error:
            if default is None:
                raise type(error)(f"Resolving {cls} failed") from error
        return default


def from_zero(name, start, count, last_values):
    """Later: add good doc"""
    return count


#  LINE: -- views -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class EnumStr1(Enum):
    def __str__(self) -> str:
        return f"{self.name.capitalize()}"


class EnumStr2(Enum):
    def __str__(self):
        return self.name


class EnumRepr1(Enum):
    def __repr__(self) -> str:
        return f"{type(self).__name__}[{self.value}]::{self}"


class EnumRepr2(Enum):
    def __repr__(self) -> str:  # CHECK: how that works for Enum
        if attributes := vars(self):
            _vars = [f"{k}={v!r}" for k, v in attributes.items()]
            return f"{type(self).__name__}[{', '.join(_vars)}]"
        return f"{type(self).__name__}{self}"


EnumStr = EnumStr2
EnumRepr = EnumRepr1
