#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = ["fire","boltons"]
# ///

from datetime import date, timedelta
from pathlib import Path

import fire
from boltons.strutils import slugify

# TASK: check what works more comfortable:
# - symlink to any/bin and execute directly from shell
# - attach to sstcore.utils_app and execute installed cli


def main() -> None:
    fire.Fire(create_empty_note)


def create_empty_note(topic: str = "daily_notes"):
    stem: str = _make_file_stem(topic)
    path: Path = _make_file_path(stem)
    template: str = _make_template(topic)
    path.write_text(template)


# LATER: Improve layout and provide template selection
def _make_template(topic: str) -> str:
    return f"""# {topic} """


# LATER: prevent accidental overrides...
# @Pathguard.unique
def _make_file_path(stem: str) -> Path:
    return Path.cwd() / f"{stem}.md"


def _make_file_stem(topic: str) -> str:
    return f"{_day_count()}_{slugify(topic)}"


# LATER: Replace this copy by original: sstcore.utils.time.day_count
def _day_count(day: date | None = None) -> int:
    day: date = day or date.today()
    delta: timedelta = day - date(2000, 1, 1)
    return delta.days


if __name__ == "__main__":
    main()
