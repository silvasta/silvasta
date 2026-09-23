"""
Start the Motor and produce the StubFile

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "StubFileMachine",
]


from enum import auto

from ...port.govern import Machine


class StubFileMachine(Machine):
    """Execute the plan and manufacture all parts of the *.pyi"""

    # TASK: what is needed?
    MD = auto()
    XML = auto()
    TXT = auto()

    def run(*args, **kwargs) -> list[str]:
        raise NotImplementedError
