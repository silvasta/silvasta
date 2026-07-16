"""
Still nice idea

- keep for the moment

"""

from typing import Any

from ...contract.log import LogDTO


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

    def success(self, text):
        self._dispatch_log("SUCCESS", text)
        super().success(text)  # Proceed with standard direct print

    def warn(self, text):
        self._dispatch_log("WARNING", text)
        super().warn(text)

    def danger(self, text):
        self._dispatch_log("ERROR", text)
        super().danger(text)

    def special(self, text):
        self._dispatch_log("INFO", text)
        super().special(text)
