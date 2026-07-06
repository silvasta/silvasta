"""
Temporary Module!

Collect ideas for Log and Print extension:
- EventBus (ultimate separation of CLI flow/visual, Core or Data execution
  - Primary target for now: passive listener
  - Future idea and goal: active interceptor
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Event:
    name: str
    payload: dict[str, Any]


class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event_name: str, callback: Callable):
        self._subscribers.setdefault(event_name, []).append(callback)

    def emit(self, event_name: str, **payload):
        event = Event(event_name, payload)
        for callback in self._subscribers.get(event_name, []):
            callback(event)


bus = EventBus()


# --- THE CORE (Ignorant of the UI) ---
def execute_agent_node(node_id: str, prompt: str):
    bus.emit("node_started", node_id=node_id)
    try:
        # ... complex LLM pipeline execution ...
        result = "Agent Response"
        bus.emit("node_success", node_id=node_id, result=result)
        return result
    except Exception as e:
        bus.emit("node_failed", node_id=node_id, error=str(e))
        raise


# --- THE VISUAL LAYER (Listens and Prints) ---
def attach_visuals(event_bus: EventBus, ui_printer):
    def on_start(event):
        ui_printer.panel(
            f"Agent {event.payload['node_id']} thinking...", frame="yellow"
        )

    def on_success(event):
        ui_printer.success(f"Agent {event.payload['node_id']} resolved.")

    event_bus.subscribe("node_started", on_start)
    event_bus.subscribe("node_success", on_success)
