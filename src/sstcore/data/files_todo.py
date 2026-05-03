import difflib
import time
from pathlib import Path

from loguru import logger


def has_diverged(workspace_file: Path, registry_file: Path) -> bool:
    """Check if the workspace file has been modified since it was registered."""
    try:
        ws_stat = workspace_file.stat()
        reg_stat = registry_file.stat()

        # If inodes differ, the IDE saved a new version.
        # If mtimes differ, the file was modified in-place.
        return (ws_stat.st_ino != reg_stat.st_ino) or (
            ws_stat.st_mtime > reg_stat.st_mtime
        )
    except FileNotFoundError:
        return True  # One of them was deleted


def show_diff(workspace_file: Path, registry_file: Path):
    ws_lines = workspace_file.read_text().splitlines()
    reg_lines = registry_file.read_text().splitlines()

    diff = difflib.unified_diff(
        reg_lines,
        ws_lines,
        fromfile=f"Registry: {registry_file.name}",
        tofile=f"Workspace: {workspace_file.name}",
        lineterm="",
    )

    for line in diff:
        print(
            line
        )  # In reality, you'd route this through your 'printer' utility


class DiffManager:
    """Handles 1-step hardlink diffing and syncing for tasks"""

    @staticmethod
    def get_diff(workspace_file: Path, registry_file: Path) -> str | None:
        """Returns unified diff if files diverged, else None."""
        try:
            ws_stat = workspace_file.stat()
            reg_stat = registry_file.stat()

            # Check if hardlink is intact and files are identical
            if (
                ws_stat.st_ino == reg_stat.st_ino
                and ws_stat.st_mtime <= reg_stat.st_mtime
            ):
                return None

            # Generate diff
            ws_lines = workspace_file.read_text().splitlines()
            reg_lines = registry_file.read_text().splitlines()

            diff = difflib.unified_diff(
                reg_lines,
                ws_lines,
                fromfile=f"Registry (Old): {registry_file.name}",
                tofile=f"Workspace (New): {workspace_file.name}",
                lineterm="",
            )
            return "\n".join(diff)

        except FileNotFoundError:
            logger.error("Missing file for diff comparison.")
            return None

    @staticmethod
    def commit_success(workspace_file: Path, registry_file: Path):
        """Forces the registry to catch up to the workspace (1-step sync)"""

        if not workspace_file.exists():
            logger.error(
                f"Cannot commit: Workspace file missing {workspace_file}"
            )
            return

        # 1. Remove the old snapshot
        if registry_file.exists() or registry_file.is_symlink():
            registry_file.unlink()

        # 2. Create the new hardlink to lock in the new state
        registry_file.hardlink_to(workspace_file)
        logger.success(
            f"State committed. Registry synced to {workspace_file.name}"
        )


def run_web_task(workspace_path: Path, registry_path: Path):

    # 1. Check for changes
    diff_text = DiffManager.get_diff(workspace_path, registry_path)
    if not diff_text:
        logger.info("No changes detected. Skipping task.")
        return

    logger.info("Changes detected. Starting web process...")

    def my_long_web_request(_text: str):
        time.sleep(55)

    # 2. Send to web process (1-5 minutes)
    try:
        response = my_long_web_request(diff_text)

        if response.status_code == 200:
            # 3. SUCCESS! Update the registry to the new baseline.
            DiffManager.commit_success(workspace_path, registry_path)
        else:
            # FAILURE. Do nothing. The old registry file remains intact.
            logger.warning("Web task failed. State not committed.")

    except Exception as e:
        logger.error(f"Task crashed: {e}. State not committed.")
