import json
from datetime import UTC, datetime
from pathlib import Path

from sqlmodel import Field, Session, SQLModel, create_engine  # ty:ignore

DB_PATH = (
    Path.home() / ".local" / "share" / "sstcore" / "global_scanner_cache.db"
)


# TASK: db_cache FROM SCANNER
# def _load_scan(cache_file: Path | None, printer: Printer, scan_root: Path) -> list[Path]:
#     # cache_file игнорируем: теперь всё в SQLite
#     records = get_recent_selections(scan_root=scan_root, limit=1)
#     if not records:
#         return []
#     record = records[0]
#     try:
#         paths_str = json.loads(record.selected_paths)
#         return [Path(p) for p in paths_str if Path(p).exists()]
#     except Exception:
#         printer.warn("Failed to read selection from cache. Starting fresh.")
#         return []
# def _save_to_cache(cache_file: Path | None, selected: list[Path], printer: Printer, filter_mode=None, extra_inc=None, extra_exc=None):
#     # cache_file игнорируем
#     try:
#         save_selection(
#             scan_root=Path.cwd(),  # или передай из folder_scanner
#             selected=selected,
#             filter_mode=filter_mode,
#             extra_include=extra_inc,
#             extra_exclude=extra_exc,
#         )
#     except Exception as e:
#         printer.warn(f"Could not save selection cache: {e}")
class SelectionRecord(SQLModel, table=True):
    __tablename__ = "selections"

    id: int | None = Field(default=None, primary_key=True)
    timestamp: str = Field(...)
    scan_root: str = Field(...)
    filter_mode: str | None = None
    filter_extra_include: str | None = None  # JSON
    filter_extra_exclude: str | None = None  # JSON
    selected_paths: str = Field(...)  # JSON


engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def save_selection(
    scan_root: Path,
    selected: list[Path],
    filter_mode: str | None = None,
    extra_include=None,
    extra_exclude=None,
):
    init_db()
    with Session(engine) as session:
        record = SelectionRecord(
            timestamp=datetime.now(UTC).isoformat(),
            scan_root=str(scan_root.resolve()),
            filter_mode=filter_mode,
            filter_extra_include=json.dumps(extra_include)
            if extra_include
            else None,
            filter_extra_exclude=json.dumps(extra_exclude)
            if extra_exclude
            else None,
            selected_paths=json.dumps([str(p) for p in selected]),
        )
        session.add(record)
        session.commit()


def get_recent_selections(
    scan_root: Path | None = None,
    limit: int = 10,
) -> list[SelectionRecord]:
    init_db()
    with Session(engine) as session:
        query = session.query(SelectionRecord).order_by(
            SelectionRecord.timestamp
        )
        if scan_root is not None:
            query = query.filter(
                SelectionRecord.scan_root == str(scan_root.resolve())
            )
        return query.limit(limit).all()
