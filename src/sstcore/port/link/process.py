"""
process

.
"""

import enum as _e

from ..govern import EnumMachine
from ._printer import printer
from .config import LinkSpec
from .data import Doc, Docs, PlugDoc, PortDoc, SidePolicy


class MergeMachine(EnumMachine):
    Schema1 = _e.auto()

    def __call__(self, docs: Docs, spec: LinkSpec | None = None) -> str:
        _spec_to_emit_and_format: LinkSpec = spec or LinkSpec()
        port: list[Doc] = []
        plug: list[Doc] = []
        fail: list[Doc] = []
        for doc in docs:
            printer.line(color="cyan")
            match doc:
                case PortDoc():
                    self.sort_for_port(doc, port, fail)
                case PlugDoc():
                    self.sort_for_plug(doc, plug, fail)
        self.handle_sort(port, plug, fail)
        match self:
            case self.Schema1:
                lines: list[str] = self.schema1(port, plug)
                return "\n".join(lines)

    def schema1(self, port: list[Doc], plug: list[Doc]) -> list[str]:
        lines: list[str] = []
        if port:
            first, *remaining = port
            self.format_port_header(first, lines)
            self.format_port_body(remaining, lines)
        if plug:
            self.format_separator(lines)
            self.format_plug_body(plug, lines)
        printer.header(f"Statsistic: Total (multi) lines: {len(lines)}")
        return lines

    def format_port_header(self, first: Doc, lines: list[str]):
        lines.append(first.text.strip("\n"))
        printer(f"Attached Port header: {first.key}")

    def format_port_body(self, remaining: list[Doc], lines: list[str]):
        for doc in remaining:
            lines.append("\n")
            attr_draw: str = f".{doc.attr}" if doc.attr else ""
            lines.append(f"[{doc.source.__name__}{attr_draw}]")
            lines.append(doc.text.strip("\n"))

    def format_separator(self, lines):
        lines.append("\n\n", "--- -- ---" * 8, "\n\n", "Implementation", "\n")

    def format_plug_body(self, plug: list[Doc], lines: list[str]):
        for doc in plug[::-1]:  # CHECK: reverse
            lines.append("\n")
            attr_draw: str = f".{doc.attr}" if doc.attr else ""
            lines.append(f"[{{{doc.source.__name__}}}{attr_draw}]")
            lines.append(doc.text.strip("\n"))

    def handle_sort(self, port: list[Doc], plug: list[Doc], fail: list[Doc]):
        printer.header(
            f"Stats: port: {len(port)}, plug: {len(plug)}, fail: {len(fail)} "
        )
        if not plug:
            printer.panel("Implementation", frame="yellow", title="Missing")
        if not port:
            printer.panel("Definitions", frame="orange", title="Missing")
        if fail:
            printer.panel(*fail, frame="red", title="Failed")

    def sort_for_port(self, doc: Doc, port: list, fail: list) -> None:
        if SidePolicy.PORT.validate(doc):
            port.append(doc)
            printer(f"Accepted: {doc.key}")
        else:
            fail.append(doc)
            printer(f"Rejected: {doc.key}")

    def sort_for_plug(self, doc: Doc, plug: list, fail: list) -> None:
        if SidePolicy.PLUG.validate(doc):
            plug.append(doc)
            printer(f"Accepted: {doc.key}")
        else:
            fail.append(doc)
            printer(f"Rejected: {doc.key}")
