"""
Provide Event definition, names and types

- Event: The Definition
- EmitFunc: Skeleton for exporting bus.emit functions
- EventNames: Select one to create Events, dispatch in bus to registered handler

"""

__all__: list[str] = [
    "Event",
    "EmitFunc",
    "CliEvent",
    "CoreEvent",
    "DataEvent",
]

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


@dataclass(frozen=True)
class Event:
    """Base payload emitted across the pipeline."""

    name: str
    sender: str
    payload: dict = field(default_factory=dict)


# IDEA: why not creating an Event locally and send it to the Bus?

# TODO: modify for preloaded shortcuts, or maybe Functor
type EmitFunc = Callable[[str, str, Any], None]


class CliEvent(StrEnum):
    INPUT_WARN = "cli.input.warn"
    RENDER_PANEL = "cli.render.panel"
    RENDER_TABLE = "cli.render.table"
    EXEC_FAIL = "cli.exec.error"


class CoreEvent(StrEnum):
    BUS_READY = "core.bus.ready"
    BUS_ERROR = "core.bus.error"
    ORCHESTRATOR_INFO = "core.orchestrator.info"


class DataEvent(StrEnum):
    REGISTRY_INFO = "data.registry.info"
    REGISTRY_WARN = "data.registry.warn"
    REGISTRY_ERROR = "data.registry.error"

    FS_UPLOAD_SUCCESS = "data.fs.success"
    FS_UPLOAD_ERROR = "data.fs.error"
