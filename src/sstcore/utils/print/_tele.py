"""
Still nice idea

- keep for the moment

"""

from collections.abc import Callable
from typing import Any

from ...contract.cli import CliDTO, CliRenderable
from ...contract.log import LogDTO
from .blueprint import Modus, Printer


class TelemetryMixin:
    """Shadows semantic printer calls to fire telemetry events before printing."""

    def __init__(self, *args, event_bus=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._event_bus = event_bus

    def _dispatch_log(self, level: str, target: Any):
        """Build and emit the LogDTO to the system bus."""
        if self._event_bus:
            # Strip Rich formatting if necessary, or let the format() method handle it
            clean_message = str(target)

            dto = LogDTO(level=level, message=clean_message)
            self._event_bus.emit(
                event_name="sys.log", sender="Printer", payload={"dto": dto}
            )

    # ---------------------------------------------------------
    # Intercept Semantic Methods
    # ---------------------------------------------------------

    def success(self: Printer, text):
        pass

        self._dispatch_log("SUCCESS", text)  # ty:ignore
        super().success(text)  # ty:ignore

    def warn(self: Printer, text):
        self._dispatch_log("WARNING", text)  # ty:ignore
        super().warn(text)  # ty:ignore

    def danger(self: Printer, text):
        self._dispatch_log("ERROR", text)  # ty:ignore
        super().danger(text)  # ty:ignore

    def special(self: Printer, text):
        self._dispatch_log("INFO", text)  # ty:ignore
        super().special(text)  # ty:ignore


class EmitMixin:
    """Intercept and convert prints to events. Leftmost in MRO → highest precedence."""

    def __init__(self, *args, emit_func: Callable | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._emit_func: Callable | None = emit_func

    def attach_emit(self, emit_func: Callable[[str, str, Any], None]) -> None:
        """Called from System.bootstrap (or manually). Accepts bus.emit or system.emit."""
        self._emit_func = emit_func
        self.wire()  # ty:ignore # switch modus

    def _emit(self, event_name: str, **payload: Any) -> None:
        if self._emit_func is not None:
            self._emit_func(event_name, sender="printer", **payload)

    def __call__(self, target: Any, **kwargs) -> None:
        """Central interception point."""
        if self.modus == Modus.EMIT and self._emit_func is not None:  # ty:ignore
            self._emit_ui_event(target, **kwargs)  # ty
            return  # short-circuit - no console output
        super().__call__(target, **kwargs)  # ty:ignore

    def _emit_ui_event(self, target: Any, **kwargs) -> None:
        if isinstance(target, CliRenderable):
            dto = target.__cli__()
        elif isinstance(target, CliDTO):
            dto = target
        else:
            dto = None

        if dto is not None:
            kind = type(dto).__name__.lower().replace("dto", "")
            self._emit(f"ui.{kind}", dto=dto, **kwargs)
        else:
            self._emit("ui.print", target=target, **kwargs)

    # Optional semantic overrides (merge your old TelemetryMixin here)
    def success(self, text: Any) -> None:
        if self.modus == Modus.EMIT and self._emit_func:  # ty:ignore
            self._emit("ui.success", message=text)
            return
        super().success(text)  # ty:ignore

    def danger(self, text: Any) -> None:
        if self.modus == Modus.EMIT and self._emit_func:  # ty:ignore
            self._emit("ui.danger", message=text)
            return
        super().danger(text)  # ty:ignore
