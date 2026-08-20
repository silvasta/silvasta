from enum import EnumMeta, IntEnum

from sstcore.port.filter import FilterEnum

from ._arg import FilterData


class _FilterBoxMeta(EnumMeta):
    def __new__(mcs, name, bases, ns):
        # 1. Start from the already-created members of FilterEnum
        #    We copy the member map so the new class gets identical members
        if FilterEnum._member_map_:
            for member_name, member in FilterEnum._member_map_.items():
                ns[member_name] = member.value  # re-create with same values

        # 2. Add / override behaviour
        def __str__(self):
            return self.name.capitalize()

        def args(self) -> FilterData:
            match self:
                case mcs.PROJECT:  # note: mcs is the future class
                    return FilterArgs(...)
                # ... all cases
                case _:
                    raise ValueError(...)

        ns["__str__"] = __str__
        ns["args"] = property(args)

        # 3. Create the class (will become an IntEnum-like)
        cls = super().__new__(mcs, name, (IntEnum,), ns)
        return cls


class FilterBox(metaclass=_FilterBoxMeta):
    """Rich filter box that re-uses the central member definitions."""

    pass
