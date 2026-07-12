import json
from datetime import UTC, datetime
from pathlib import Path

from sqlmodel import Field, Session, SQLModel, create_engine  # ty:ignore

DB_PATH = (
    Path.home() / ".local" / "share" / "sstcore" / "global_scanner_cache.db"
)


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
            SelectionRecord.timestamp.desc()
        )
        if scan_root is not None:
            query = query.filter(
                SelectionRecord.scan_root == str(scan_root.resolve())
            )
        return query.limit(limit).all()
