"""
Launch cli_tools with SafeTyper and the full System in action

Amazing
- scanner: Select in tui filetree from scanned folder and merge to summary file

Useful
- monitor: Log Console with live updates from file (new with .jsonl)
- print: Read Markdown and print with Rich

"""

# NEXT: what else??

from .console.tools import cli_tools


def main() -> None:
    cli_tools()


if __name__ == "__main__":
    main()
