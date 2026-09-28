"""
process

.
"""

import functools as _f
import typing as _t
from types import SimpleNamespace

from ..raising import SstCoreError
from .data import DocMerger


class EasyBase(SimpleNamespace):
    """Stable Base for all Easy Member"""

    _types = {}
    _specs = {}

    def __init_subclass__(cls, role=None, id=None, **kwargs):
        super().__init_subclass__(**kwargs)
        action = "Added"
        if role == "type":
            EasyBase._types[id] = cls
        elif role == "spec":
            EasyBase._specs[id] = cls
        else:
            action = "Ignored"
        cls._emit_default(f"{cls.__name__}: {action} {role}: {id}")

    def spawn(self, type_id, spec_id):
        if type_id not in self._types or spec_id not in self._specs:
            raise ValueError("Invalid type or spec identifier.")

        base_cls = self._types[type_id]
        mixin_cls = self._specs[spec_id]

        name = f"{type_id.capitalize()}{spec_id.capitalize()}Tool"
        _cls = type(name, (mixin_cls, base_cls, EasyBase), {})

        print(f"[Spawner] Generated {name}")
        return _cls()

    _emit: _t.Callable | None = None

    def emit(self, *args, **kwargs):
        (self._emit or self._emit_default)(*args, **kwargs)

    @staticmethod
    def _emit_default(*args, **kwargs):
        print(*args, **kwargs)


class EasyCatchL1(EasyBase, role="spec", id="catch"):
    def dispatch(self, *args, **kwargs):
        with self:
            return super().dispatch(*args, **kwargs)

    def __enter__(self) -> _t.Self:
        self.emit(f"{self}: Executing Pipeline in Context")
        return self

    def __exit__(self, exception_type, exception_value, _exception_trace_back):
        self.emit(f"{self}: Closing context")

        if exception_type is None:
            self.emit(f"{self}: No Issues...")
            return True

        self.emit(f"{self}: {(error := exception_type.__name__)}")

        if issubclass(exception_type, SstCoreError):
            self.emit(f"Critical! {error=}")
            return False

        if issubclass(exception_type, (AttributeError, TypeError)):
            self.emit(f"Continue... {exception_value=}")
            return True

        return True  # LATER: configured handling


class EasyCoreL1[Core: _t.Callable](EasyBase, role="spec", id="core"):
    """Stable Core for all Easy Member"""

    core: Core
    # TODO:
    __core__: Core

    def __call__(self, *args, **kwargs):
        return (
            self.core(*args, **kwargs)
            if hasattr(self, "core")
            else self.__core__(*args, **kwargs)
        )


class Dunders(dict):
    def __init__(self, dunders: set[str]):
        for method in dunders:
            self[method] = None

    def __setitem__(self, key, _value=None):
        """Assign pairs of {target: __target__}"""
        super().__setitem__(key.strip("_"), f"__{key.strip('_')}__")
        print(f"- {type(self).__name__}: Setting {key}")  # REMOVE: after debug


class EasyAccessL1(EasyBase, role="spec", id="get"):
    """Dot Access on all Dunders"""

    dunders: set[str] = {
        "__doc__",
        "__func__",
        "__links__",
    }
    _methods: Dunders  # LATER: targets:dict, for splitted base

    def __init__(self, dunders: set[str] | None = None, **kwargs):
        self.dunders: set[str] = (dunders or set()) | self.dunders
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == "dunders":
            self._methods = Dunders(self.dunders)

    def __getattr__(self, name: str) -> _t.Callable:
        self.emit(f"[{self}].__getattr__: {name}")  # REMOVE: after debug
        if method := self._methods.get(name):
            return _f.partial(self.invoke, attribute=method)
        raise AttributeError(f"Fail in __getattr__: {name}", self._methods)


class InjectorBase[Core](EasyCatchL1, EasyCoreL1, role="type", id="inject"):
    __call__: Core


class CollectorBase[Core](EasyCatchL1, role="type", id="collect"):
    __call__: Core


class ReflectorBase[Core](EasyCoreL1, role="type", id="reflect"):
    __call__: Core


class ProcessorBase[Core](EasyCoreL1, role="type", id="proc"):
    __call__: Core


class _Reflect(ReflectorBase, EasyAccessL1):
    def core(self, target, /, attr: str):
        raw = self.strategy(target, attr)
        return self.clean(raw) if attr == "__doc__" else raw


class _Inject(InjectorBase, EasyAccessL1):
    __call__: Injecting

    def core(self, target, value, /, attr: str):
        return self.strategy(self.resolve(target, attr), value, attr)

    def direct(self, target, value, attr: str):
        object.__setattr__(target, attr, value)

    def polite(self, target, value, attr: str):
        setattr(target, attr, value)


#  LINE: -- Testing -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def merger(source: str, target: str, /, joint: str = "") -> str:
    return f"""{source}{joint}{target}"""


def test_dunder_access():
    dunders: set[str] = {  # TODO: auto update on (lined) access?
        "__doc__",
        "__func__",
        "__links__",
    }
    d1 = Dunders(set())
    print_topic("d1", d1)

    # d2
    d2 = Dunders(dunders)
    print_topic("d2", d2)
    d2["log"] = "no_dunder"
    print_topic("d2", lined(d2))
    updates = {"__port_doc__", "__rich__"}
    d2.update(Dunders(updates))
    print_topic("d2", lined(d2))

    access1 = EasyAccessL1()
    print_topic("Easy1", access1)
    access2 = EasyAccessL1({"test", "__cli_", "__log__"})
    print_topic("Easy2", access2)


def lined(target, /):
    return "\n".join(f"{k}: {v}" for k, v in target.items())


def print_topic(title, content, /):
    print(title)
    print(content)
    print()


def test_family_tree():
    base = EasyBase()
    print_topic(base, "--- -- ---" * 5)
    print_topic("specs", lined(base._specs))
    print_topic("types", lined(base._types))

    proc: ProcessorBase[DocMerger] = ProcessorBase(
        state="running", core=merger
    )
    c = proc((), ())
    print_topic(proc, "--- -- ---" * 5)
    print_topic("specs", lined(proc._specs))
    print_topic("types", lined(proc._types))

    reflect = proc.spawn("reflect", "get")
    print_topic("reflect", reflect)


if __name__ == "__main__":
    # test_family_tree()
    test_dunder_access()
