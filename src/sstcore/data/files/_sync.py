"""
Provide Container for Files and Tools for FileSystem Operations

                                                       DependencyLevel[0]
"""

# TASK: test this, together with ListVault, inside sachmis

__all__: list[str] = [
    "FileSyncMixin",
]


from functools import singledispatchmethod
from pathlib import Path
from typing import Any, Self

from loguru import logger
from pydantic import BaseModel

from ...error import NotImplementedDispatchError
from ...port.files import File, PathS, SyncMode, SyncRegister
from ...port.link import portlink
from ...util.path.guard import PathGuard
from ...util.path.guard._operate import Copy, Rotate, TransferStrategy
from ._file import SstFile


@portlink(SyncRegister)
class FileSyncMixin[File: SstFile]:
    """Execute File System Operations supported by PathGuard"""

    root_dir: Path  # REMOVE:
    files: list[File]  # REMOVE:

    mode: PathGuard.SyncMode = SyncMode.IGNORE  # NEXT: PolicyField

    def mirror_from_path(
        self, source: PathS, mode: SyncMode = SyncMode.IGNORE
    ) -> list[File]:
        """Copy external files from into local_root and add to registry"""
        self.mode: SyncMode = SyncMode.resolve(mode)

        return self._sync_external_files(
            source,
            transfer_strategy=TransferStrategy(
                func=PathGuard.copy, name="Copy"
            ),
        )

    def absorb_from_path(
        self, source: PathS, mode: SyncMode = SyncMode.IGNORE
    ) -> list[File]:
        """Move external files from into local_root and add to registry"""
        self.mode: SyncMode = SyncMode.resolve(mode)

        return self._sync_external_files(
            source,
            transfer_strategy=PathGuard.rotate,  # LATER:
        )

    def mirror_from_registry(
        self, external: Self, mode: SyncMode = SyncMode.IGNORE
    ) -> list[File]:
        """Copy files of external registry into local_root and attach"""
        self.mode: SyncMode = SyncMode.resolve(mode)

        return self._sync_registry(external, transfer_strategy=Copy)

    def absorb_from_registry(
        self, external: Self, mode: SyncMode = SyncMode.INCREMENT
    ) -> list[File]:
        """Move files of external registry into local_root and attach"""
        self.mode: SyncMode = SyncMode.resolve(mode)

        return self._sync_registry(external, transfer_strategy=Rotate)  # LATER:

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Workers
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    @singledispatchmethod
    def _sync_external_files(
        self,
        source: Path | list[Path],
        transfer_strategy: TransferStrategy,
    ) -> list[File]:
        """Mirror or Absorb external file source, dispatch file or dir"""
        raise NotImplementedDispatchError(source, transfer_strategy)

    @_sync_external_files.register
    def _(
        self,
        source: list,
        transfer_strategy: TransferStrategy,
    ) -> list[File]:
        """Concat multiple file sources"""
        return [
            file
            for path in source
            for file in self._sync_external_files(
                source=path,
                transfer_strategy=transfer_strategy,
            )
        ]

    @_sync_external_files.register
    def _(
        self,
        source: Path,
        transfer_strategy: TransferStrategy,
    ) -> list[File]:
        """Mirror or Absorb external file source, dispatch file or dir"""

        if source.is_dir():
            temp_registry: Self = self.clone_empty_registry(source)
            temp_registry.attach_local_files()  # ty:ignore FIX: derive
            return self._sync_registry(
                external=temp_registry,
                transfer_strategy=transfer_strategy,
            )
        if source.is_file():
            if file := self._fetch_external_file(
                source,
                transfer_strategy=transfer_strategy,
            ):
                return [file]

        action: str = getattr(transfer_strategy, "__name__", "Task")
        logger.error(f"Nothing to do for {action}! Invalid path: {source=}")
        return []

    def _sync_registry(
        self,
        external: Self,
        transfer_strategy: TransferStrategy,
    ) -> list[File]:
        """Attach data from external registry"""

        new_files: list[File] = []

        for file in external.files:
            source: Path = external.root_dir / file.path

            if new_file := self._fetch_external_file(
                source,
                new_local_path=file.path,
                transfer_strategy=transfer_strategy,
            ):
                new_files.append(new_file)

        logger.info(f"Files attached: {len(new_files)=}")

        # LATER: return Result: {new,increment,override,ignore}
        # - multiple lists to handle, attached, [SyncMode], not found

        return new_files

    def _fetch_external_file(
        self,
        source: Path,
        transfer_strategy: TransferStrategy,
        new_local_path: Path | str | None = None,
    ) -> File | None:
        """Copy or Move file into local_root and load new File into registry"""
        # CHECK: something looks strange... SyncMode still needed?

        target: Path = self.root_dir / (new_local_path or source.name)

        if result := transfer_strategy.synced(source, target, mode=self.mode):
            return self.attach_from_path(result)  # ty:ignore FIX: derive

        if self.mode == SyncMode.IGNORE:
            logger.debug(f"skipping existing file: {target.name}")
            return None

        if self.mode == SyncMode.OVERRIDE:
            self.clear(files_to_clear=target)  # ty:ignore FIX: clear from vault

        return self.attach_from_path(target)  # ty:ignore FIX: derive

    #  LINE: -- clone -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def clone_empty_registry(
        self,
        local_root: Path,
        /,
        *,
        exclude: set[str] | None = None,
        add_to_exclude: set[str] | None = None,
        exclude_unset=False,
    ) -> Self:
        """Get registry with same configuration, new local_root and No files"""

        if exclude is None:
            exclude: set[str] = {"files", "local_root"}

        if add_to_exclude:
            exclude: set[str] = exclude | add_to_exclude

        if not isinstance(self, BaseModel):
            raise NotImplementedError(f"BaseModel required for {self}")

        cloned_data: dict[str, Any] = self.model_dump(
            exclude=exclude, exclude_unset=exclude_unset, mode="python"
        )

        # Intercept the serialized scanner and update its target root
        if (scanner_data := cloned_data.get("scanner")) is not None:
            if isinstance(scanner_data, dict):
                scanner_data["scan_root"] = local_root
            else:
                # Fallback just in case model_dump left it as an object
                scanner_data.scan_root = local_root

        return type(self)(local_root=local_root, **cloned_data)
