"""
Start the Motor and produce the StubFile

                                                 DependencyLevel[0]
"""

from pathlib import Path

__all__: list[str] = [
    "StubFileMachine",
]


import subprocess
import tempfile
from collections import defaultdict
from collections.abc import Iterable

from ...port.annotate import StubJobDTO4
from ...util.path.guard import StubFileGuard


class StubFileMachine:
    """Manufacturing engine for generating, verifying, and persisting .pyi stub files."""

    @classmethod
    def execute(
        cls, jobs: Iterable[StubJobDTO4], dry_run: bool = False
    ) -> list[Path]:
        """
        Execute a collection of StubJobDTO4 specifications.

        Orchestrates sub-stub creation, ensures directory invariants via PathGuard,
        and aggregates export lines into the target package __init__.pyi.
        """
        written_paths: list[Path] = []
        package_index_map: dict[Path, list[str]] = defaultdict(list)

        for job in jobs:
            content = job.renderer(job.source_target, job.class_prefix)

            stub_file: Path = StubFileGuard.single_stub_file(
                job.target_module, prefix=job.class_prefix
            )
            init_file: Path = StubFileGuard.get_stub_dir(job.target_module)

            # 1. Atomic write of the specific stub
            if not dry_run:
                cls._safe_write(stub_file, content)
            written_paths.append(stub_file)

            # 2. Record export line for package index
            import_statement = (
                f"from .{job.sub_dir}._{job.class_prefix.lower()} import {job.class_prefix}Empty\n"
                f"{job.public_symbol}: {job.class_prefix}Empty"
            )
            package_index_map[init_file].append(import_statement)

        # 3. Synchronize package index stubs (__init__.pyi)
        for init_path, export_entries in package_index_map.items():
            cls._update_init_stub(init_path, export_entries, dry_run=dry_run)
            written_paths.append(init_path)

        # 4. Optional ruff format pass over generated paths
        if not dry_run and written_paths:
            cls._format_targets(written_paths)

        return written_paths

    @staticmethod
    def _safe_write(target: Path, content: str) -> None:
        """Write through PathGuard using an atomic exchange pattern."""

        # EXTRACT:
        with tempfile.NamedTemporaryFile(
            "w", dir=target.parent, delete=False, suffix=".tmp"
        ) as tmp:
            tmp.write(content)
            temp_path = Path(tmp.name)

        temp_path.replace(target)

    @classmethod
    def _update_init_stub(
        cls, init_path: Path, entries: list[str], dry_run: bool
    ) -> None:
        # EXTRACT:
        """Ensure public symbols are exported cleanly in package __init__.pyi."""
        header = '"""Auto-generated Type Stubs by StubFileMachine."""\n\n'
        body = "\n\n".join(entries) + "\n\n__all__: list[str] = [\n"
        for entry in entries:
            # extract binding name
            binding = entry.split(":")[-2].strip().split("\n")[-1]
            body += f'    "{binding}",\n'
        body += "]\n\n"
        body += "def __getattr__(name: str) -> Any: ...\n"

        full_content = header + "from typing import Any\n\n" + body
        if not dry_run:
            cls._safe_write(init_path, full_content)

    @staticmethod
    def _format_targets(paths: Iterable[Path]) -> None:
        # EXTRACT:
        # EXTRACT:
        # EXTRACT:
        """Execute ruff format if available on the system."""
        try:
            str_paths = [str(p) for p in paths]
            subprocess.run(
                ["ruff", "format", *str_paths],
                capture_output=True,
                check=False,
            )
        except FileNotFoundError:
            pass  # Ruff optional at machine level
