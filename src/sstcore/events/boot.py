from sstcore.utils.print import Printer

from .bus import EventBus

# NEXT: check boot: build_event_system - answer to alice!!


def build_event_system(printer: Printer, logger_handler=None):
    bus = EventBus()
    if logger_handler:
        bus.subscribe("sys.log", logger_handler)
    bus.subscribe("ui.panel", lambda e: printer(e.payload["target"]))
    bus.subscribe("ui.table", lambda e: printer(e.payload["target"]))
    return bus


# События: используй префиксы, чтобы сразу видеть домен:
# sys.log, sys.error, sys.warn — системные логи;
# ui.panel, ui.table, ui.line — UI‑события;
# data.load, data.save — операции с данными.


# IDEA:
# class SafeTyper:
#     self.event_bus = build_event_system(self.printer, handle_log_event)
