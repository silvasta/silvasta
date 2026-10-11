import typing
from dataclasses import asdict, dataclass
from typing import Self

CLASSES: set[str] = {
    "cli",
    "log",
}


@typing.dataclass_transform(kw_only_default=True)
class EventDTO:
    """Base class for all DTOs. Automatically makes subclasses dataclasses."""

    registry: dict[str, type[Self]] = {}

    def __init_subclass__(cls, name: str, **kwargs):
        super().__init_subclass__(**kwargs)

        if name in cls.registry:
            raise TypeError(f"Duplicated Class! {name=} cache: {cls.registry}")
        cls.registry[name] = cls

        dataclass(kw_only=True, **kwargs)(cls)

    @classmethod
    def spawn(cls, name: str) -> type[Self]:
        if missing := CLASSES - cls.registry.keys():
            raise RuntimeError(f"Missing Classes! [{missing}]({cls.registry})")
            # LATER: warning for other misssing, error for 'name'a missing
        return cls.registry[name]

    @classmethod
    def cli(cls) -> type[CliDTO]:
        return cls.spawn("cli")  # ty:ignore

    @classmethod
    def Cli(cls) -> type[CliDTO]:  # noqa:N802
        return cls.registry["cli"]  # ty:ignore

    @classmethod
    def Log(cls, *args, **kwargs) -> LogDTO:  # noqa:N802
        assert issubclass(log := cls.registry["log"], LogDTO)
        return log(*args, **kwargs)

    @classmethod
    def SPECIAL(cls, **typed: asdict(SpecialCliDTO)) -> SpecialCliDTO:  # noqa:N802
        # IDEA: TypedDict, but then, syncing with DTO?
        assert issubclass(special := cls.registry["special"], SpecialCliDTO)
        return special(**typed)


class CliDTO(EventDTO, name="cli"):
    username: str
    email: str
    age: int | None = None


class LogDTO(EventDTO, name="log"):
    username: str
    email: str
    age: int | None = None


class SpecialCliDTO(CliDTO, name="special"):
    """Panel, Table, ..."""

    department_code: str


#  LINE: -- Tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --


CliDTO(
    username="peter",
    email="p@g.com",
)

EventDTO.cli()(
    username="peter",
    email="p@g.com",
)

EventDTO.Cli()(
    username="peter",
    email="p@g.com",
)

EventDTO.Log(
    username="peter",
    email="p@g.com",
)
EventDTO.Log("missing", failed_input=5)

EventDTO.SPECIAL()
