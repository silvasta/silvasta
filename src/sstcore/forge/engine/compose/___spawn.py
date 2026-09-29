"""
process

.
"""

import functools as _f
import typing as _t
from types import SimpleNamespace

from ....port.raising import SstCoreError


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

    @classmethod
    def mix(cls, type_id, spec_id):
        if type_id not in cls._types or spec_id not in cls._specs:
            raise ValueError("Invalid type or spec identifier.")

        # TASK: better selection, or delete (copy idea to foree.mix)
        base_cls = cls._types[type_id]
        mixin_cls = cls._specs[spec_id]

        name = f"{type_id.capitalize()}{spec_id.capitalize()}Tool"
        _new_cls = type(name, (mixin_cls, base_cls, EasyBase), {})

        print(f"[Spawner] Generated {name}")
        return _new_cls()

    @classmethod
    def spawn(cls, type_id, /) -> type[_t.Self]:
        if not (operator := cls._types.get(type_id)):
            raise ValueError("Invalid type or spec identifier.")

        print(f"[Spawner] From Registry: {operator}")

        return operator

    _emit: _t.Callable | None = None

    def emit(self, *args, **kwargs):
        (self._emit or self._emit_default)(*args, **kwargs)

    @staticmethod
    def _emit_default(*args, **kwargs):
        pass
        # print(*args, **kwargs)


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
    __core__: Core

    def __call__(self, *args, **kwargs):
        return (
            self.core(*args, **kwargs)
            if hasattr(self, "core")
            else self.__core__(*args, **kwargs)
        )


class EasyAccessL1(EasyBase, role="spec", id="get"):
    """Dot Access on all Dunders"""

    dunders: set[str] = {
        "__doc__",
        "__func__",
        "__links__",
    }
    _methods: dict

    def __init__(self, dunders: set[str] | None = None, **kwargs):
        self.dunders: set[str] = (dunders or set()) | self.dunders
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == "dunders":
            self._methods: frozenset = self.Dunders(self.dunders)

    def __getattr__(self, name: str) -> _t.Callable:
        if method := self._methods.get(name):
            return _f.partial(self.invoke, attribute=method)
        raise AttributeError(f"Fail in __getattr__: {name}", self._methods)


class PortOperator(
    EasyCatchL1, EasyAccessL1, EasyCoreL1, role="type", id="operator"
): ...


class InjectorBase[Core](EasyCatchL1, EasyCoreL1, role="type", id="injector"):
    __call__: Core


class CollectorBase[Core](EasyCatchL1, role="type", id="collector"):
    __call__: Core


class ReflectorBase[Core](EasyCoreL1, role="type", id="reflector"):
    __call__: Core


class ProcessorBase[Core](EasyCoreL1, role="type", id="proc"):
    __call__: Core


if __name__ == "__main__":
    ...
