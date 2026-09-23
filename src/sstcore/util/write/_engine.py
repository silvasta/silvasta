"""
Start the Motor and produce the StubFile

                                                 DependencyLevel[0]
"""

from pathlib import Path

__all__: list[str] = [
    "StubFileMachine",
]


from enum import auto

from ...port.annotate import StubJobDTO
from ...port.govern import Machine
from ...util.path.guard import StubFileGuard


class StubFileMachine(Machine):
    """Execute the plan and manufacture all parts of the *.pyi"""

    TYPE = auto()

    def run(*args, **kwargs) -> list[str]:
        raise NotImplementedError(args, kwargs)


class StubFileMachine1(Machine):
    """Executes the high-frequency fabrication of .pyi files based on DTOs"""

    @classmethod
    def _render_stub(cls, job: StubJobDTO) -> str:
        """Translate DTO into Python source code string."""
        lines = [f"class {job.class_name}:"]

        for attr, typ in job.attributes.items():
            lines.append(f"    {attr}: {typ}")

        for method in job.methods:
            params = ", ".join(
                [f"{p.name}: {p.annotation}" for p in method.params]
            )
            lines.append(
                f"    def {method.name}(self, {params}) -> {method.return_type}: ..."
            )

        if len(lines) == 1:
            lines.append("    ...")

        return "\n".join(lines) + "\n"

    @classmethod
    def run(cls, job: StubJobDTO, dry_run: bool = False) -> None:

        content = cls._render_stub(job)
        file: Path = StubFileGuard.get_stub_dir(job.target_module)

        if dry_run:
            print(f"--- Would write to {file} ---", "\n", content)
            return

        file.write_text(data=content)
