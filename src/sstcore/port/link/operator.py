"""
Operators - The mix

- temporary module
"""

import typing as _t

from ._printer import printer
from .base import EasyAccessL1, EasyBase, EasyCatchL1, EasyCoreL1
from .define import DocMerger, Injecting, Reflecting

_specs = (  # INFO: temporary, most likeley to delete
    EasyCatchL1,
    EasyAccessL1,
    EasyCoreL1,
    EasyBase,
)


class PortOperator[Core: _t.Callable](
    # IMPORTANT: order!!! and, all needed??? at minimub EasyBase
    EasyCatchL1,
    EasyAccessL1,
    EasyCoreL1[Core],
    EasyBase,
):
    """Mixed Base for all Easy Member"""

    _member: dict[str, type[_t.Self]] = {}  # IDEA: dict[Literal[...]:type]

    def __init_subclass__(cls, id: str):
        super().__init_subclass__()  # LATER: final check for: **kwargs
        if id in cls._member:
            raise RuntimeError(f"Duplicated Member: {cls} in {cls._member=}")
        cls._member[id] = cls
        cls._emit_default(f"{cls.__name__}: Registered: {id}")

    @classmethod
    def mix(cls, type_id, spec_id):
        # TASK: better selection, or delete (most likely overkill here...)
        # - use when here not all BasesL1 mixed in
        if type_id not in cls._member or spec_id not in _specs:
            raise ValueError("Invalid type or spec identifier.")
        base_cls = cls._member[type_id]
        mixin_cls = _specs[spec_id]  # NOTE: if used, then as slice or similar
        name = f"{type_id.capitalize()}{spec_id.capitalize()}Tool"
        _new_cls = type(name, (mixin_cls, base_cls, EasyBase), {})
        print(f"[Spawner] Generated {name}")
        return _new_cls()

    @classmethod
    def spawn(cls, type_id, /) -> type[_t.Self]:
        # IDEAS: direct shortcuts for members?
        # - Approach 1: PortOperator.reflect(...)
        # - Approach 2: more explicit
        # @property; def spawn(self)->Spawner:...
        # -> with spawner: member as properties like:
        # PortOperator.spawn.reflect(...)
        # PortOperator.spawn.inject(...)
        if operator := cls._member.get(type_id):
            print(f"[{cls.__name__}] Spawn from Registry: {operator.__name__}")
            return operator
        raise ValueError("Invalid type or spec identifier.")

    @property
    def spown(self) -> Spawner:  # REMOVE: name, just for better comparison now
        # NOTE: should be enough for isinstanciated PortOperator,
        # otherwise the class-level property? usually too error prone...
        return Spawner(registry=self._member)


class Spawner[T: type]:
    # IDEA:@property def reflector(self) -> ReflectorProto: ...# new proto
    # IDEA:@property def reflector(self) -> Reflector: ... # Original
    # IDEA:@property def reflector(self) -> Operator[Reflecting]: ... # parametrized + existing proto
    """Provide extended access for presets"""

    def __init__(self, registry: dict[str, T]):
        self.registry: dict[str, T] = registry

    def _core(self, type_id: str) -> T:
        if operator := self.registry.get(type_id):
            print(f"[Spawner] Spawn from Registry: {operator.__name__}")
            return operator
        raise ValueError("Invalid type or spec identifier.")

    @property
    def reflector(self) -> PortOperator:
        return self._core(type_id="reflector")  # ty:ignore

    # NOTE: use some cast if ever used like that
    @property
    def injector(self) -> InjectorBase:
        return self._core(type_id="injector")  # ty:ignore


#  LINE: -- Pipeline -- -- - -- -- - -- -- - -- -- - -- -- - -- --

# AI: here is the question, do they all need the full BaseMix?
# - other question would be, why not? what hurts?
# - some strategy for that would definitely be fine
# - the PortOperator.mix? slightly overkill but as example or test?


class ReflectorBase(PortOperator[Reflecting], id="reflector_base"):
    """Collect the Detecting and Extracting Methods"""


class InjectorBase(PortOperator[Injecting], id="injector_base"):
    """Collect the Modificating Methods with Safety"""


class CollectorBase[Core: _t.Callable](
    PortOperator[Core], id="collector_base"
):
    """Run the MRO pipelines and Reflect and Inject data"""


#  LINE: -- Processor -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class ProcessorBase[Core](PortOperator, id="processor"):
    """Most likely independent of the others here..."""


#  LINE: -- Testing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def merger(source: str, target: str, /, joint: str = "") -> str:
    return f"""{source}{joint}{target}"""


def test_family_tree():
    with printer.topic("PortOperator"):
        _operator = PortOperator()
        printer.panel("PortOperator.Member")
        printer.lines(_operator._member)

    with printer.topic("Processor"):
        proc: ProcessorBase[DocMerger] = ProcessorBase(
            state="running", core=merger
        )
        empty = proc((), ())
        printer.section("empty", empty)
        printer.debug(proc)

    with printer.topic("Processor"):
        reflect = _operator.spawn("reflector_base")()
        printer.section("reflect", reflect)

    with printer.topic("Spawn"):
        Inject = _operator.spawn("injector_base")
        printer(Inject.__mro__)
        inject = Inject(mode="soft", merge=merger)
        # TODO: inject = _operator.spown.injector(mode="soft", merge=merger)
        printer.section("inject", inject)
        printer.debug(inject)
        printer.header("MRO")


def lined(target, /):
    if isinstance(target, dict):
        target = (f"{k}: {v}" for k, v in target.items())
    return "\n".join(target)


def print_topic(title, content=None, /):
    print(title)
    if content:
        print(content)
    print()


if __name__ == "__main__":
    test_family_tree()
