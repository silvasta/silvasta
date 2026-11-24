"""
Reflective Loader & Full Generic Spectrum Resolution

- moved here from the port as the small helper went out of control

"""

__all__: list[str] = [
    "LoaderTypes",
    "ReflectiveLoader",
    "resolve_loader_types",
]

from dataclasses import dataclass
from typing import Any

from sstcore.port.empty import VOID, MayNot
from sstcore.port.primitives._loader import Loader as _PortLoader

from ..reflect import _typearg
from ..reflect.___signature import extract_signature_types
from ..reflect._typearg import extract_type_args, format_type_arg


class ReflectiveLoader[**P, T](_PortLoader[P, T]):
    """Upgraded Loader using brick.reflect for deep MRO TypeVar substitution."""

    if not _typearg.preserves_generic_alias_on_instance():

        def __class_getitem__(cls, params: Any) -> Any:
            return _typearg.remembering_getitem(cls, params)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _typearg.normalize_orig_bases(cls)

    @property
    def type_args(self) -> LoaderTypes:  # ty:ignore FIX:
        return resolve_loader_types(self)


@dataclass(frozen=True, slots=True)
class LoaderTypes:
    """Spectrum plus the resolved ``(P, T)`` pair."""

    specs: tuple[_typearg.GenericSpec, ...]
    value: Any
    parameters: Any
    value_source: str
    parameters_source: str
    func_return: Any = VOID
    func_parameters: Any = VOID
    default_type: Any = VOID

    def render(self) -> str:
        value = "UnTyped" if self.value is VOID else format_type_arg(self.value)
        return f"{format_type_arg(self.parameters)}, {value}"

    def summary(self) -> str:
        explicit = ", ".join(str(spec) for spec in self.specs if spec.explicit)
        generic: str = explicit or "-"
        return f"{self.render()} via {self.value_source}; generic=[{generic}]"


def _declared_spec(
    specs: tuple[_typearg.GenericSpec, ...], origins: tuple[type, ...]
) -> MayNot[_typearg.GenericSpec]:
    for spec in specs:
        if any(spec.is_to_declare(o) for o in origins):
            return spec
    return None


def _pick_value(
    declared: _typearg.GenericSpec | None,
    func_return: Any,
    default_type: Any,
) -> tuple[Any, str]:
    declared_value = VOID if declared is None else declared.get("T")

    if _typearg.is_concrete_type(declared_value):
        return declared_value, "generic"
    if _typearg.is_concrete_type(func_return):
        return func_return, "func"
    if default_type is not VOID:
        return default_type, "default"
    if _typearg.is_type_parameter(declared_value):
        return declared_value, "unbound"

    return VOID, "none"


def _pick_parameters(
    declared: _typearg.GenericSpec | None,
    func_parameters: Any,
) -> tuple[Any, str]:
    if declared is not None:
        declared_parameters = declared.get("P")
        if declared_parameters is not VOID:
            return declared_parameters, "generic"

    if func_parameters is not VOID:
        return func_parameters, "func"

    return Ellipsis, "unknown"


def _looks_generic(target: Any) -> bool:
    """Any Target in the MRO declaring type parameters or generic bases?"""

    if not isinstance(target, type):
        return True
    if getattr(target, "__orig_class__", None) is not None:
        return True

    for _type in _type_instance(target).__mro__:
        if getattr(_type, "__type_params__", ()):
            return True
        if getattr(_type, "__orig_bases__", ()):
            return True
    return False


def _type_instance(target: object) -> type:
    return target if isinstance(target, type) else type(target)


def resolve_loader_types(loader: _PortLoader[Any, Any]) -> LoaderTypes:
    """Merge generic specialization with a loader's runtime channels."""
    specs = extract_type_args(loader) if _looks_generic(loader) else ()
    declared = _declared_spec(specs, (ReflectiveLoader, _PortLoader))

    func_parameters: Any = VOID
    func_return: Any = VOID
    if loader._func is not None:
        func_parameters, func_return = extract_signature_types(loader._func)

    if loader._default is VOID:
        default_type: Any = VOID
    elif loader._default is None:
        default_type = None
    else:
        default_type = type(loader._default)

    value, value_source = _pick_value(declared, func_return, default_type)
    parameters, parameters_source = _pick_parameters(declared, func_parameters)
    return LoaderTypes(
        specs=specs,
        value=value,
        parameters=parameters,
        value_source=value_source,
        parameters_source=parameters_source,
        func_return=func_return,
        func_parameters=func_parameters,
        default_type=default_type,
    )
