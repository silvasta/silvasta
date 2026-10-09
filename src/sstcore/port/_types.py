"""
Group TypeDefs as Classes and Merge them to Modules

- bundle loose type definitions for the Registry,...
- belongs technically to their corresponding port module
- import from the corresponding port module, not from here!

                                                 DependencyLevel[-]
"""

__all__: list[str] = [
    "custom_types",
    "registry_types",
]

from dataclasses import dataclass, field
from types import ModuleType
from typing import Any, TypeAliasType

custom_types: ModuleType


def _dunder_format(item: str, /) -> str:
    return f"__{_dunder_extract(item)}__"


def _dunder_extract(item: str, /) -> str:
    return str(item).strip("_")


@dataclass
class ModuleDTO:
    """Collect the Data for Constructing 1 Module"""

    # IDEA: use _dunder_format(ModuleDTO.attrs...) at the end

    name: str | None = None
    doc: str | None = None
    file: str | None = None  # IDEA: just this ._types file?
    _all_: list[str] | None = None  # AI: this might be import for typing?

    # NOTE: this is probably assembled at the end
    _dict_: dict[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        """True == Ready for Assemble"""
        checks_ok: tuple[bool, ...] = (
            self.name is not None,
            self.doc is not None,  # unsure, maybe add some default?
            # TODO: compare _all_ and _dict_?
        )
        return all(checks_ok)


def modulizer[T = RegistryTypes](cls: type[T]) -> ModuleType:
    # INFO: using T=RegistryTypes until debug finished, later on:
    # def modulizer[T](cls: type[T]) -> ModuleType:
    """Transform Class into Module"""

    # Extract Data (move to ModuleDTO.extract,classmethod?)
    module_data = ModuleDTO(
        name=_format_name(clsname=cls.__name__),
        doc=cls.__doc__,
        file=__file__,  # LATER: maybe more dynamic (if modulizer gets exported)
        # _all_= RENDERED! from __dict__
        _dict_=_extract_types(cls=cls),
    )
    if module_data:
        return _render_module(module_data)
    raise ValueError(f"Modulizer Failed! {cls=}, {module_data=}")


# IDEA: ModuleDTO.render(...) | classmethod?
def _render_module(data: ModuleDTO) -> ModuleType:
    # AI_TASK: here the module should be rendered
    raise NotImplementedError


def _extract_types[T](cls: type[T]) -> dict[str, TypeAliasType]:
    """Extract type=... definitions"""
    cls_types: dict[str, TypeAliasType] = {}
    for type_name, alias in cls.__dict__.items():
        if isinstance(type_name, TypeAliasType):
            cls_types[type_name] = alias
    return cls_types


def _format_name(clsname: str) -> str:
    """PascalCase to snake_case, dependency-free"""
    if not clsname:
        raise ValueError("Got empty class name")
    result: list[str] = [clsname[0].lower()]
    for c in clsname[1:]:
        if c.islower():
            result.append(c)
        else:
            result.append(f"_{c.lower()}")
    return "".join(result)


class RegistryTypes:
    """
    Collect all Types for the Registry:

    - Definition: port.register
    - Production: brick.vault
    - Manufactur: forge.registry (not already exists)

    """

    type Key = str
    type Index = int | slice


# AI: here probably the _types.pyi should override?
registry_types: ModuleType = modulizer(cls=RegistryTypes)


# IDEA: 2 - just derive ModuleType??
# AI_QUESTION: is this maybe way easier for the same result??
class OtherRegistryTypes(ModuleType):
    """
    Collect all Types for the Registry:

    - Definition: port.register
    - Production: brick.vault
    - Manufactur: forge.registry (not already exists)

    """

    type Key = str
    type Index = int | slice


registry_types = OtherRegistryTypes("registry_types")
