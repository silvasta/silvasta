import os
import tempfile
from dataclasses import fields, is_dataclass
from datetime import UTC, datetime
from pathlib import Path


class MarkdownReportMixin:
    @property
    def markdown(self) -> str:
        """Pure view: renders current container state as GitHub-Flavored Markdown."""
        items = list(self)
        title = type(self).__name__
        ts = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        lines = [
            f"# {title} Snapshot",
            f"*Generated: {ts} | Count: {len(items)}*",
            "",
        ]

        if not items:
            lines.append("_Empty_")
            return "\n".join(lines)

        # Extract rows from dataclasses, dicts, or generic objects
        first = items[0]
        if is_dataclass(first):
            headers = [f.name for f in fields(first)]
            rows = [[getattr(item, h) for h in headers] for item in items]
        elif isinstance(first, dict):
            headers = list(first.keys())
            rows = [[item.get(h, "") for h in headers] for item in items]
        else:
            headers = ["Value"]
            rows = [[repr(item)] for item in items]

        def esc(val) -> str:
            return str(val).replace("|", "\\|").replace("\n", " ")

        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in rows:
            lines.append("| " + " | ".join(esc(v) for v in row) + " |")

        return "\n".join(lines)

    def _repr_markdown_(self) -> str:
        return self.markdown

    def dump_report(self, path: str | Path = "state_report.md") -> Path:
        """1-trigger atomic write to disk."""
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        content = self.markdown

        # Atomic write via temp file + os.replace so live Markdown previews never flicker
        fd, tmp_path = tempfile.mkstemp(dir=target.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp_path, target)
        except BaseException:
            Path(tmp_path).unlink(missing_ok=True)
            raise
        return target
