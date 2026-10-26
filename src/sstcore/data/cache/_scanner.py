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
from typing import ClassVar, Self

from diskcache import Cache

from ...port.link import portlink
from ...port.printer import Print
from ...port.scanner import PresetInfo, ScanCaching
from ...util.path.guard import PathGuard
from ...util.print import Printer

type Record = tuple[list[Path], datetime]


@portlink(ScanCaching)
class DiskScanCache:
    """DiskCache for local Scanner storage"""

    LAST: ClassVar[str] = "__last__"

    def __init__(
        self, cache_dir: Path, scan_root: Path, printer: Print | None
    ) -> None:
        self._cache_dir = cache_dir
        self._scan_root = scan_root.resolve()
        self._printer: Print = printer or Printer()  # ty:ignore will match soon
        self._cache = Cache(self._cache_dir)

    @property
    def scan_root(self) -> Path:
        return self._scan_root

    def _key(self, name: str) -> tuple[str, str]:
        return (str(self._scan_root), name)

    def load(self, name: str = LAST) -> list[Path]:
        try:
            record: Record | None = self._cache.get(self._key(name))
            if record:
                return PathGuard.absolute(
                    record[0], self._scan_root, filter_exists=True
                )
        except Exception as error:
            text = f"Failed to read scanner cache ({name}): {error}"
            self._printer.warn(text)
        return []

    def save(
        self,
        selected: Iterable[Path],
        name: str = LAST,
        *,
        update_last: bool = True,
    ) -> None:
        rel_paths = PathGuard.relative(selected, self._scan_root, strict=False)
        payload: Record = (rel_paths, datetime.now(UTC))
        root_tag = str(self._scan_root)
        try:
            if update_last or name == self.LAST:
                self._cache.set(self._key(self.LAST), payload, tag=root_tag)
            if name != self.LAST:
                self._cache.set(self._key(name), payload, tag=root_tag)
        except Exception as error:
            self._printer.warn(f"Selection Save to Cache failed: {error}")

    def exists(self, name: str = LAST) -> bool:
        return self._key(name) in self._cache

    def names(self, *, include_last: bool = False) -> Sequence[str]:
        root_str = str(self._scan_root)
        names: list[str] = []
        for key in self._cache:
            if isinstance(key, tuple) and len(key) == 2 and key[0] == root_str:
                if not include_last and key[1] == self.LAST:
                    continue
                names.append(key[1])
        return sorted(names)

    def presets(self, *, include_last: bool = False) -> dict[str, PresetInfo]:
        presets: dict[str, PresetInfo] = {}
        for name in self.names(include_last=include_last):
            record: Record | None = self._cache.get(self._key(name))
            if record is not None:
                rel_paths, updated_at = record
                valid = PathGuard.absolute(
                    rel_paths, self._scan_root, filter_exists=True
                )
                presets[name] = PresetInfo(
                    name=name,
                    paths=tuple(valid),
                    updated_at=updated_at,
                )
        return presets

    def delete(self, name: str) -> bool:
        return bool(self._cache.delete(self._key(name)))

    def clear(self) -> int:
        return self._cache.evict(tag=str(self._scan_root))

    def prune(self) -> int:
        pruned = 0
        for name in self.names(include_last=True):
            record: Record | None = self._cache.get(self._key(name))
            if record is None:
                continue
            rel_paths, updated_at = record
            valid = PathGuard.absolute(
                rel_paths, self._scan_root, filter_exists=True
            )
            if len(valid) < len(rel_paths):
                pruned += len(rel_paths) - len(valid)
                new_rel = PathGuard.relative(
                    valid, self._scan_root, strict=False
                )
                self._cache.set(
                    self._key(name),
                    (new_rel, updated_at),
                    tag=str(self._scan_root),
                )
        return pruned

    def close(self) -> None:
        self._cache.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _type, error: BaseException | None, _tb) -> None:
        if error:
            self._printer(error)
        self.close()
