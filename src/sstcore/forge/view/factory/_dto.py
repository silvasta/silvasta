"""
CliFactory - Experiment 2

- Frozen dataclasses and stringly arguments

"""

from dataclasses import dataclass, fields
from typing import Any

from ....port.event.dto import CliDTO, PanelDTO, TableDTO

# AI: this was so far not detailed inspected


@dataclass(frozen=True, slots=True)
class CliProducer:
    # root: DtoFactory

    def __call__(self, content: Any, **kwargs: Any) -> CliDTO:
        return self._build(self.root.types.cli, content, kwargs)

    def panel(self, content: Any, **kwargs: Any) -> PanelDTO:
        return self._build(self.root.types.panel, content, kwargs)

    def _build(self, cls: type, content: Any, kwargs: dict[str, Any]):
        kwargs = dict(kwargs)
        kwargs.setdefault("style", self.root.policy.default_style)
        known = {f.name for f in fields(cls)}
        extra = {k: kwargs.pop(k) for k in list(kwargs) if k not in known}
        if extra:
            match self.root.policy.unknown:
                case "error":
                    raise TypeError(f"Unknown args: {extra}")
                case "meta":
                    kwargs.setdefault("meta", {})["unknown_args"] = extra
                case "drop":
                    pass
        try:
            return cls(content=content, **kwargs)
        except TypeError:
            if self.root.policy.strict:
                raise
            allowed = {k: v for k, v in kwargs.items() if k in known}
            allowed.setdefault("meta", {})["error"] = "partial construct"
            return cls(content=content, **allowed) @ dataclass(
                frozen=True, slots=True
            )


class TableProducer:
    # root: DtoFactory

    def __call__(
        self,
        content: list[list[Any]],
        *,
        col_names: list[str] | None = None,
        row_names: list[str] | None = None,
        corner: str = "",
        **style: Any,
    ) -> TableDTO:
        return self.root.types.table(
            content=content,
            col_names=col_names or [],
            row_names=row_names or [],
            corner=corner,
            **self._style(style),
        )

    def from_col_dicts(
        self, cols: dict[str, list[Any]], **style: Any
    ) -> TableDTO:
        return self(
            [list(row) for row in zip(*cols.values(), strict=True)],
            col_names=list(cols.keys()),
            **style,
        )

    def from_row_dicts(self, rows: dict[str, Any], **style: Any) -> TableDTO:
        return self(list(rows.values()), row_names=list(rows.keys()), **style)

    def from_value_dicts(
        self,
        rows: list[dict[str, Any]],
        headers: list[str] | None = None,
        **style: Any,
    ) -> TableDTO:
        if not rows:
            return self([], **style)
        headers = headers or list(
            dict.fromkeys(k for row in rows for k in row)
        )
        return self(
            [[row.get(h, "") for h in headers] for row in rows],
            col_names=headers,
            **style,
        )

    def _style(self, style: dict[str, Any]) -> dict[str, Any]:
        style.setdefault("style", self.root.policy.default_style)
        return style
