"""
Keep Data in temporary Storage

                                    DependencyLevel.sstcore.data[0]
"""

__all__: list[str] = [
    "DiskScanCache",
]

from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, NamedTuple, Self

import diskcache

from ...port.link import portlink
from ...port.printer import Print
from ...port.scanner import PresetInfo, ScanCaching
from ...util.path.guard import PathGuard
from ...util.print import Printer


@portlink(ScanCaching)
class DiskScanCache:
    """DiskCache for local Scanner storage"""

    LAST: ClassVar[str] = "__last__"

    def __init__(
        self, cache_dir: Path, scan_root: Path, printer: Print | None = None
    ) -> None:
        """Assume given Paths are verified and ready"""
        self.scan_root: Path = scan_root
        self._print: Print = printer or Printer()
        self._cache = diskcache.Cache(directory=cache_dir)

    class _Key(NamedTuple):
        tag: str
        name: str

    def _key(self, name: str = LAST) -> _Key:
        return self._Key(f"{self.scan_root}", name)

    def find(self, name: str | None = LAST) -> _Record | None:
        """Reject None but apply LAST for "" (empty string)"""
        if name is None:
            return None
        if raw := self._cache.get(self._key(name=name or self.LAST)):
            return _Record(*raw)

    def load(self, name: str | None = LAST) -> list[Path]:
        try:
            if record := self.find(name):
                return record.absolute(self.scan_root, filter_exists=True)
        except Exception as error:
            self._print.warn(f"Failed to read scanner cache ({name}): {error}")
        return []

    def save(
        self,
        selected: Iterable[Path],
        name: str = LAST,
        *,
        update_last: bool = True,
    ) -> None:
        value: _Record = _Record.now(paths=selected, local_root=self.scan_root)
        try:
            if update_last or name == self.LAST:
                self._cache.set(self._key(), value, tag=f"{self.scan_root}")
            if name != self.LAST:
                self._cache.set(self._key(name), value, tag=f"{self.scan_root}")
        except Exception as error:
            self._print.warn(f"Saving Selection to Cache failed: {error}")

    def __contains__(self, name: str = LAST) -> bool:
        return self._key(name) in self._cache

    def names(self, *, include_last: bool = False) -> Sequence[str]:
        return sorted(
            key.name
            for item in self._cache
            if (key := self._Key(*item)).tag == f"{self.scan_root}"
            and (include_last or key.name != self.LAST)
        )

    def presets(self, *, include_last: bool = False) -> dict[str, PresetInfo]:
        presets: dict[str, PresetInfo] = {}
        for name in self.names(include_last=include_last):
            if record := self.find(name):
                presets[name] = record.to_preset(name, self.scan_root)
        return presets

    def delete(self, name: str) -> bool:
        return bool(self._cache.delete(self._key(name)))

    def clear(self) -> int:
        return self._cache.evict(tag=f"{self.scan_root}")

    def prune(self) -> int:
        pruned = 0
        for name in self.names(include_last=True):
            if (record := self.find(name)) is None:
                continue
            if (valid := record.valid(self.scan_root)) == record:
                continue
            pruned += len(record.paths) - len(valid.paths)
            self._cache.set(
                self._key(name), value=valid, tag=f"{self.scan_root}"
            )
        return pruned

    def close(self) -> None:
        self._cache.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _type, error: BaseException | None, _tb) -> None:
        if error:
            self._print(error)
        self.close()


class _Record(NamedTuple):
    """Define proper input/output to Cache"""

    paths: list[Path]
    time: datetime

    @classmethod
    def now(cls, paths: Iterable[Path], local_root: Path | None = None) -> Self:
        """_Record with current UTC and optional trim paths to local_root"""
        return cls(
            paths=PathGuard.relative(paths, local_root, strict=False)
            if local_root
            else list(paths),
            time=datetime.now(UTC),
        )

    def to_preset(self, name: str, local_root: Path, /) -> PresetInfo:
        """Bridge internal Record to public PresetInfo"""
        return PresetInfo(
            name=name,
            paths=tuple(self.absolute(local_root, filter_exists=True)),
            updated_at=self.time,
        )

    def absolute(
        self, local_root: Path, /, filter_exists: bool = False
    ) -> list[Path]:
        """Resolve to absolute paths and optional drop missing files"""
        return PathGuard.absolute(
            self.paths, local_root, filter_exists=filter_exists
        )

    def valid(self, local_root: Path, /) -> Self:
        """Check FileSystem existance and drop missing paths"""
        return self._replace(
            # NEXT: check if works
            paths=PathGuard.relative(
                self.paths,
                root=local_root,
                existing=True,
            )
        )
