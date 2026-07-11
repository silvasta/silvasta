from dataclasses import dataclass

import fire
from pydantic import BaseModel

from sstcore.config import ConfigManager
from sstcore.core import System
from sstcore.events import EventBus
from sstcore.utils import Printer
from sstcore.utils.view.dto import CliDTO, LogDTO, PanelDTO, TableDTO
from sstcore.utils.view.protocol import CliRenderable, LogSerializable


def main():
    fire.Fire(SystemExamples)


class SystemExamples:
    def __init__(self):
        self._system: System = System.bootstrap()

    @property
    def _config(self) -> ConfigManager:
        return self._system.config

    @property
    def _printer(self) -> Printer:
        return self._system.printer

    @property
    def _bus(self) -> EventBus:
        return self._system.bus

    def _emit(self, event_name: str, sender: str, **payload) -> None:
        """Increase convenience for bus access"""
        self._bus.emit(event_name, sender, **payload)

    def protocol(self):
        check_protocol_on_instance(self._printer)

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### gcf1

    def basic(self):
        emit_basic(self)

    def sys(self):
        emit_via_system(self)

    def log(self):
        emit_log_dto(self)

    def raw(self):
        emit_raw(self)

    def multi(self):
        emit_multiple(self)

    ### gcf1
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### alice

    def simple(self):
        emit_simple(self._system)

    def metric(self):
        emit_with_metrics(self._system)

    def panel(self):
        emit_ui_panel(self._system, agent=LLMConversationAgent())

    def tele(self):
        emit_global_telemetry(self._system)

    def error(self):
        emit_error_context(self._system)

    ### alice
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### g31

    def table(self):
        demo_4_cli_table(self)

    def tele2(self):
        demo_5_telemetry_monitoring(self)

    # --- Mode 4: UI Table ---
    def tdto(self):
        """Emit a Table DTO rendering."""
        stats = SystemHealthStats()
        self._emit("ui.table", sender="G3.1", target=stats)

    # --- Mode 5: UI Line / Raw ---
    def line(self):
        target = "[bold green]This is a success message![/bold green]"
        self._emit("ui.line", "g3", target=target)

    ### g35f
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### g420

    # ==================== EMIT EXAMPLES ====================
    def base(self):
        """Simple string events."""
        self._emit("sys.info", "basic_test", message="Hello from basic emit")
        self._emit(
            "ui.line",
            "basic_test",
            message="This is a simple line",
            style="green",
        )
        self._printer.success("Basic emit test completed")

    def object(self):
        agent = LLMConversationAgent()
        task = SimpleTask(id="task-123", status="running", progress=0.75)

        self._emit("ui.panel", "object_test", target=agent)  # -> CliRenderable
        self._emit(
            "sys.log", "object_test", target=agent
        )  # -> LogSerializable
        self._emit("ui.panel", "object_test", target=task)
        self._emit("sys.log", "object_test", target=task)

        self._printer.success("Object emit test completed")

    def dto(self):
        """Emit pre-built DTOs directly (useful for precise control)."""
        dto = LogDTO(
            message="Manual DTO test",
            level="WARNING",
            metrics={"custom": 42, "source": "test"},
            extra={"batch_id": "BATCH-2026-07-10"},
        )
        self._emit("sys.log", "dto_test", target=dto)
        self._printer.success("Raw DTO test completed")

    def struc(self):
        """Structured logging with metrics/extra data."""
        self._emit(
            "sys.log",
            "metrics_test",
            message="Processing batch",
            level="INFO",
            metrics={"items": 150, "success_rate": 0.94, "errors": 3},
            extra={"batch_id": "BATCH-2026-07-10", "tags": ["prod", "daily"]},
        )
        self._printer.success("Metrics emit test completed")


def check_protocol_on_instance(printer: Printer):
    agent = LLMConversationAgent()
    if isinstance(agent, CliRenderable):
        printer.success(f"Agent is {CliRenderable}")
    if isinstance(agent, LogSerializable):
        printer.success(f"Agent is {LogSerializable}")


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### gcf1


def emit_basic(self):
    """Direct emit with raw payload."""
    self._bus.emit("ui.panel", "test", target=LLMConversationAgent())


def emit_via_system(self):
    """Using the convenience wrapper on System."""
    self._system.emit("ui.line", "script", message="hello from system wrapper")


def emit_log_dto(self):
    """Emit something that should go through the log bridge."""
    self._bus.emit("sys.log", "test", target=LLMConversationAgent())


def emit_raw(self):
    """Bypass __cli__/__log__ entirely."""
    self._bus.emit("ui.markdown", content="# Raw content", sender="manual")


def emit_multiple(self):
    """Show fan-out to multiple handlers."""
    agent = LLMConversationAgent()
    self._bus.emit("ui.panel", "test", target=agent)
    self._bus.emit("sys.log", "test", target=agent)
    self._bus.emit("sys.warn", "test", message="something happened")


### gcf1
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### alice


def emit_simple(system: System):
    system.bus.emit(
        "sys.log", sender="test", message="Простая отладочная запись"
    )


def emit_with_metrics(system: System):
    system.bus.emit(
        "sys.log",
        sender="test",
        message="Метрики процесса",
        metrics={"cpu": 42, "memory_mb": 128},
    )


def emit_ui_panel(system: System, agent):
    system.bus.emit("ui.panel", sender="test", target=agent)


def emit_global_telemetry(system: System):
    system.bus.emit("internal.heartbeat", sender="test", tick=123)


def emit_error_context(system: System):
    try:
        _ = 1 / 0
    except ZeroDivisionError as e:
        system.bus.emit(
            "sys.error",
            sender="test",
            message="Произошла ошибка",
            exception=e,
            context={"step": "preprocess"},
        )


### alice
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### g35f


def demo_4_cli_table(self):
    """Emit arbitrary table configurations as dynamic structured tables."""
    self._printer.title("Demo 4: Table Data Representation", style="blue")

    table_dto = TableDTO(
        title="SST System Metrics Overview",
        data=[
            {"Engine": "sachmis", "Latency": "142ms", "Memory": "42MB"},
            {
                "Engine": "gpt-translator",
                "Latency": "820ms",
                "Memory": "12MB",
            },
            {
                "Engine": "pipeline-runner",
                "Latency": "12ms",
                "Memory": "108MB",
            },
        ],
        headers=["Engine", "Latency", "Memory"],
        style="cyan",
    )

    self._bus.emit("ui.table", sender="Dashboard", target=table_dto)


def demo_5_telemetry_monitoring(self):
    """Demonstrate real-time global telemetry pipeline intercepting all active streams."""
    self._printer.title(
        "Demo 5: Broadcast to Telemetry Monitors", style="green"
    )
    # Emit random operational actions to show global subscribers in action
    self._bus.emit(
        "ui.line", sender="AgentEngine", target="Ping status check..."
    )
    self._bus.emit(
        "sys.log", sender="TelemetryWatch", target="System integrity 100%"
    )


### g35f
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class LLMConversationAgent(BaseModel):
    name: str = "sachmis"
    system_prompt: str = "bla bla..\n" * 500
    message_history: list[dict] = []
    tokens_used: int = 25
    is_active: bool = True

    def __log__(self) -> LogDTO:
        return LogDTO(
            message=f"Agent: {self.name} loaded",
            level="INFO",
            metrics={
                "Tokens": self.tokens_used,
                "Messages": len(self.message_history),
            },
            extra={},
        )

    def __cli__(self) -> CliDTO:
        return PanelDTO(
            title=f"Agent: {self.name}",
            content="create proper DTO first",
            metrics={
                "Tokens": self.tokens_used,
                "Messages": len(self.message_history),
            },
            frame="yellow",
        )


class SystemHealthStats(BaseModel):
    cpu_temp: float = 45.5
    ram_usage: int = 2048
    active_connections: int = 12

    def __cli__(self) -> TableDTO:
        # Note: Ensure TableDTO in your codebase matches this or update FormatMixin
        return TableDTO(
            title="System Health Monitor",
            headers=["Metric", "Value"],
            data=[
                ["CPU Temp", f"{self.cpu_temp}°C"],
                ["RAM Usage", f"{self.ram_usage} MB"],
                ["Connections", str(self.active_connections)],
            ],
        )


@dataclass
class SimpleTask:
    """Second example class (dataclass style). Demonstrates protocol usage."""

    id: str
    status: str = "pending"
    progress: float = 0.0

    def __log__(self) -> LogDTO:
        return LogDTO(
            message=f"Task {self.id} updated",
            level="INFO",
            metrics={"progress": self.progress, "status": self.status},
        )

    def __cli__(self) -> PanelDTO:
        return PanelDTO(
            title=f"Task {self.id}",
            content=f"Status: {self.status}",
            metrics={"progress": f"{self.progress:.0%}"},
            frame="blue",
        )


if __name__ == "__main__":
    main()
