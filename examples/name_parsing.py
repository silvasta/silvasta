"""
Show examples in isolated environment without any deeper purpose

- Platform to test and show Parsed Names and Styles

"""

from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Any

import fire
from pydantic import BaseModel

from sstcore.config import ConfigManager
from sstcore.core import System, fetch_system
from sstcore.events import EventBus
from sstcore.utils import NamePattern, Printer, day_count, printer
from sstcore.utils.parse import ParsedName, StyledName

# TODO: finish wiring
sst: System = fetch_system(_allow_uninitialized=True)

config: ConfigManager = sst.config
bus: EventBus = sst.bus
_printer: Printer = sst.printer  # LATER: replace below?

pattern1: str = "{day}_summary.{suffix}"


def main():
    printer.title("Start of name_parsing")
    fire.Fire(ParseTasks)


def view(obj: Any):
    printer(str(obj))
    printer(repr(obj))
    printer(obj)


class ParseTasks:
    def pattern(self):
        view(NamePattern(pattern1))

    def base(self):
        parsed_name()

    def style(self):
        styled_name()

    def regex(self):
        pattern_namer()

    def error(self):
        show_error()

    def model(self):
        parsed_basemodel_name()


def parsed_name():
    printer.title("Start of parsed_name")

    pattern: str = "{day}_summary.{suffix}"
    summary_file: ParsedName = ParsedName(pattern=pattern)
    printer(summary_file)

    # Fine
    printer.header(summary_file({"day": str(day_count()), "suffix": "md"}))
    printer.header(summary_file("9607_summary.md"))

    with suppress(ValueError):
        printer.danger(summary_file({"suffix": "md"}))

    printer.header(summary_file("962_summary.md"))

    with suppress(ValueError):
        printer.success(summary_file("962_summary_1.md"))
        printer.success("it works!")


def styled_name():

    sstfile_dates: StyledName = StyledName.parse_style(
        style_pattern=(
            "[{style1}]{name}[/]: [{style2}]{first_tracked}[/]"
            " - [{style3}]{last_updated}[/]"
        ),
        keys=["name", "first_tracked", "last_updated"],
        styles=["blue", "red", "white"],
    )

    # printer(sstfile_dates) # ERROR: rich.errors.MarkupError
    print(sstfile_dates)

    print(sstfile_dates.styled(["file.pdf", datetime.now(), "22-03-2026"]))
    printer(sstfile_dates.styled(["file.pdf", datetime.now(), "22-03-2026"]))


def parsed_basemodel_name():
    printer.title("Start of parsed_basemodel_name")

    class TreeInfoSchema(BaseModel):
        sprout_id: int
        topic: str

    # Instantiate with the generic type and schema class
    tree_parser: ParsedName[TreeInfoSchema] = ParsedName[TreeInfoSchema](
        pattern="t_{sprout_id}_{topic}",
        model_cls=TreeInfoSchema,
        strip_extension=True,  # Safely handles Path("t_42_math.json")
    )
    # Backwards parsing returns the BaseModel directly!
    tree_data = tree_parser(Path("t_42_math.json"))

    printer("tree_data", end=": ")
    printer(tree_data)
    printer(f"{tree_data}")
    printer(f"{tree_data=}")

    printer(tree_data.sprout_id)  # 42 (as int)
    printer(tree_data.topic)  # "math"

    printer(tree_parser)


def pattern_namer():
    namer = NamePattern("{date}_{topic}_sstcore.{suffix}")

    printer(namer)

    name_1: dict[str, str] = {
        "date": f"{day_count()}",
        "topic": "arboreal",
        "suffix": "md",
    }
    forward: str = namer.format(**name_1)
    printer(forward)

    backward: dict[str, str] = namer.extract(forward)
    printer(backward)

    random_fine: dict[str, str] = namer.extract("9598_code_sstcore.py")
    printer(random_fine)

    with suppress(ValueError):
        random_bad: dict[str, str] = namer.extract("9_code_stcore.py")
        printer(random_bad)

    random_1: dict[str, str] = namer.extract("93-59_sstcore_sstcore.p")
    printer(random_1)


def show_error():
    pattern = "{day}_summary.{suffix}"
    summary_name: ParsedName = ParsedName(pattern=pattern)
    printer(summary_name)

    printer(f"{(summary_name([22, 'md']))=}")

    summary_fail = "hello_summary-tar-gz"
    try:
        _fail_name_parts: dict = summary_name(summary_fail)
    except ValueError:
        printer.danger(f"Failed for {summary_fail=}")

    summary_file = "422_summary.tar.gz"
    fail_key = "hello"
    try:
        printer(f"{(name_parts:= summary_name(summary_file))=}")
        printer(f"{name_parts["suffix"]=}")
        printer(f"{name_parts[fail_key]=}")
    except KeyError:
        printer.danger(f"Failed with {fail_key=} for {summary_file=}")


if __name__ == "__main__":
    main()
