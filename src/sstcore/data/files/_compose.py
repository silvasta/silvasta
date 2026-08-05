"""
Assemble the File Registry.

-
"""

__all__: list[str] = [
    "RegistryBuilder",
    "SstFileRegistry",
    # TODO:
]

from dataclasses import dataclass
from pathlib import Path
from types import new_class
from typing import TYPE_CHECKING, Any, Literal, cast, overload

from pydantic import BaseModel, ConfigDict, Field

from ...port.builder import Builder, TypedBuilder
from ...port.registry import ListingRegistry
from ...utils.registry import ListRegistry
from ...utils.view import Cli, Log, Repr, Rich, Str, ViewBuilder, view
from ._file import SstFile
from .proto import (  # REMOVE:
    FilePathOps,
    FileQueryOps,
    FileScanOps,
    FileSyncOps,
)

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Bases
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

# TODO: select 1, pydantic/else


class _FilePathMixin[FilesT: SstFile]:
    local_root: Path
    items: list[FilesT]

    def __init__(
        self,
        local_root: Path,
        items: list[FilesT] | None = None,
        **kwargs: Any,
    ) -> None:
        self.local_root = local_root
        self.items = items or []
        # cooperative: only call super if next defines __init__
        super().__init__(**kwargs) if hasattr(super(), "__init__") else None


class _FilePathMixin(BaseModel):
    local_root: Path
    items: list[Any] = Field(default_factory=list)
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ModelListRegistry[ItemT](ListRegistry[ItemT], BaseModel):
    items: list[ItemT] = Field(default_factory=list)
    model_config = ConfigDict(arbitrary_types_allowed=True)


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Slots
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


@dataclass(frozen=True, slots=True)
class Slot[P]:
    """
    One composition step.

    mixin:    runtime implementation (may be a class or a factory of a class)
    protocol: structural type this step guarantees on the result (doc + TYPE_CHECKING)
    """

    mixin: type
    protocol: type[P]
    name: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            object.__setattr__(self, "name", self.mixin.__name__)


class RegistryBuilder[ItemT: SstFile, P]:
    """
    Assemble a file registry class from ListRegistry + capability slots.

    Example:
    -------
    cls = (
        RegistryBuilder(SstFile)
        .essential()
        .with_scan()
        .with_sync()
        .with_model()
        .build()
    )
    reg = cls(local_root=Path("."), items=[])
    """

    def __init__(self, item_type: type[ItemT]) -> None:
        self._item_type: type[ItemT] = item_type
        self._slots: list[Slot[Any]] = []
        self._use_model: bool = False
        self._class_name: str = f"{item_type.__name__}Registry"
        self._extra_bases: list[type] = []

    # ----- fluent config -------------------------------------------------

    def named(self, name: str) -> RegistryBuilder[ItemT, P]:
        self._class_name: str = name
        return self

    def with_model(self, enabled: bool = True) -> RegistryBuilder[ItemT, P]:
        self._use_model: bool = enabled
        return self

    def add(
        self, mixin: type, protocol: type[P] | None = None
    ) -> RegistryBuilder[ItemT, P]:
        self._slots.append(Slot(mixin=mixin, protocol=protocol or mixin))
        return self

    def add_slot(self, slot: Slot[Any]) -> RegistryBuilder[ItemT, P]:
        self._slots.append(slot)
        return self

    def essential(self) -> RegistryBuilder[ItemT, P]:
        """Identity + path + query — minimum useful file registry."""
        from ._mixins import FileIdentityMixin, FilePathMixin, FileQueryMixin

        return (
            self.add(FileIdentityMixin, ListingRegistry)
            .add(FilePathMixin, FilePathOps)
            .add(FileQueryMixin, FileQueryOps)
        )

    def with_scan(self) -> RegistryBuilder[ItemT, P]:
        from ._mixins import FileScanMixin

        return self.add(FileScanMixin, FileScanOps)

    def with_sync(self) -> RegistryBuilder[ItemT, P]:
        from ._mixins import FileSyncMixin

        return self.add(FileSyncMixin, FileSyncOps)

    # ----- assembly ------------------------------------------------------

    # TODO: select 1
    def _bases(self) -> tuple[type, ...]:
        """
        MRO order: capability mixins (LIFO of addition? FIFO?) → ListRegistry → BaseModel?

        FIFO of .add() means first added is farthest from ListRegistry
        if we reverse for standard 'mixin left' MRO.

        We want: Sync, Scan, Query, Path, Identity, ListRegistry, [BaseModel]
        essential() adds Identity, Path, Query — then with_scan, with_sync.
        So reverse(slots) + ListRegistry + optional Model.
        """
        mixins: list[type] = [s.mixin for s in self._slots]
        ordered: list[type] = [*reversed(mixins), ListRegistry]
        if self._use_model:
            ordered.append(BaseModel)
        ordered.extend(self._extra_bases)
        return tuple(ordered)

    # TODO: select 1
    def _bases(self) -> tuple[type, ...]:
        mixins = [s.mixin for s in reversed(self._slots)]
        # IMPORTANT: collect the Protocol as well!
        if self._use_model:
            # Mixins are BaseModel subclasses; ListRegistry is plain —
            # put ListRegistry before Model only if ListRegistry has no fields.
            # Pattern: *mixins (models), ModelListBridge
            return tuple(mixins) + (ModelListRegistry,)
        return tuple(mixins) + (ListRegistry,)

    def build(self) -> type[Any]:
        bases: tuple[type, ...] = self.bases()
        item_type: type[ItemT] = self._item_type
        class_name = self._class_name

        def _body(namespace: dict[str, Any]) -> None:
            namespace["__annotations__"] = {}
            namespace["items"] = (
                Field(default_factory=list) if self._use_model else []
            )

            namespace["__module__"] = __name__
            namespace["_item_type"] = item_type

            def _create_local_file(self, local_path: Path) -> ItemT:
                return item_type(local_path=local_path)

            namespace["_create_local_file"] = _create_local_file

        cls: type = new_class(class_name, bases, kwds={}, exec_body=_body)

        cls.__registry_slots__ = tuple(self._slots)
        cls.__registry_item_type__ = item_type
        return cls

    # ----- typed products (what you export) ------------------------------

    def build_core(self) -> type[FileQueryOps[ItemT]]:
        self._slots.clear()
        self.essential().with_model(True)
        return cast(type[FileQueryOps[ItemT]], self.build())

    def build_scan(self) -> type[FileScanOps[ItemT]]:
        self._slots.clear()
        self.essential().with_scan().with_model(True)
        return cast(type[FileScanOps[ItemT]], self.build())

    def build_full(self) -> type[FileSyncOps[ItemT]]:
        self._slots.clear()
        self.essential().with_scan().with_sync().with_model(True)
        return cast(type[FileSyncOps[ItemT]], self.build())

    @overload
    def product(
        self, preset: Literal["core"]
    ) -> type[FileQueryOps[ItemT]]: ...
    @overload
    def product(self, preset: Literal["scan"]) -> type[FileScanOps[ItemT]]: ...
    @overload
    def product(self, preset: Literal["full"]) -> type[FileSyncOps[ItemT]]: ...
    @overload
    def product(self, preset: None = None) -> type[Any]: ...
    # TODO: simplify
    def product(self, preset: Preset | None = None) -> type[Any]:  # TODO: type
        if preset == "core":
            return self.build_core()
        if preset == "scan":
            return self.build_scan()
        if preset == "full":
            return self.build_full()
        return self.build()


_FilesView = ViewBuilder(
    cli=Cli.PATHS,
    str=Str.MODULE,
    rich=Rich.NAME,
    repr=Repr.OFF,
    log=Log.DATA,
)


@view(cli=Cli.PATHS, str=Str.MODULE, rich=Rich.NAME, log=Log.DATA)
class _FilesView:
    @property
    def _panel_paths(self: Files) -> list[Path]:
        return list(self.paths())


FileRegistry = RegistryBuilder(SstFile).named("SstFileRegistry").build_core()

FileScanRegistry = (
    RegistryBuilder(SstFile).named("SstFileRegistryScan").build_scan()
)
SstFileRegistry = (
    RegistryBuilder(SstFile).named("SstFileRegistryFull").build_full()
)

FullRegistry = RegistryBuilder(SstFile).build_full()
reg = FullRegistry(local_root=Path("data/files"), items=[])

type Preset = Literal["full", "scan", "core"]

if TYPE_CHECKING:
    _instance_check: Builder = RegistryBuilder()
    _class_check: type[Builder] = RegistryBuilder
    #
    _instance_check: TypedBuilder = RegistryBuilder()
    _class_check: type[TypedBuilder] = RegistryBuilder
