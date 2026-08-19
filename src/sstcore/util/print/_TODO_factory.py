from enum import Enum, auto
from typing import Any, Literal, Protocol, overload


# 1. Define your isolated Protocols
class ConsolePrinter(Protocol):
    def print_to_console(self) -> None: ...


class FilePrinter(Protocol):
    def print_to_file(self) -> None: ...


# 2. Define the Enum
class PrinterMode(Enum):
    CONSOLE = auto()
    FILE = auto()
    # ... 3 more ...


# 3. The Factory Builder
class PrinterFactory:
    # Static Overloads map the Enum member to the Protocol
    @overload
    def build(self, mode: Literal[PrinterMode.CONSOLE]) -> ConsolePrinter: ...

    @overload
    def build(self, mode: Literal[PrinterMode.FILE]) -> FilePrinter: ...

    # ... 3 more overloads ...

    # The actual runtime implementation
    def build(self, mode: PrinterMode) -> Any:
        """Dynamically build the specific printer type"""
        if mode == PrinterMode.CONSOLE:
            cls = type(
                "DynamicConsole",
                (),
                {"print_to_console": lambda self: print("Console")},
            )
            return cls()
        elif mode == PrinterMode.FILE:
            cls = type(
                "DynamicFile",
                (),
                {"print_to_file": lambda self: print("File")},
            )
            return cls()
        raise ValueError("Unknown mode")
