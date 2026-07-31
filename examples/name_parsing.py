"""
Show examples in isolated environment without any deeper purpose

- Platform to test and show Parsed Names and Styles

"""

from contextlib import suppress
from typing import Any

import fire

from sstcore import ConfigManager, System
from sstcore.system.event import EventBus
from sstcore.utils import Printer, day_count
from sstcore.utils.parse import ParsedName, SchemaName
from sstcore.utils.parse.name import NamePattern

sst: System = System.bootstrap()
config: ConfigManager = sst.config
bus: EventBus = sst.bus
printer: Printer = sst.printer

pattern1: str = "{day}_summary.{suffix}"


def latest_schema_name():
    pattern = "t_{id}_{topic}"
    schema = SchemaName(pattern=pattern)

    printer(str(schema))
    printer(schema)
    printer(f"{schema!r}")

    name = "t_33_validation"
    printer(schema(name))

    keys = (11, "test")
    printer(schema(keys))


def main():
    printer.title("Start of name_parsing")
    fire.Fire(ParseTasks)


def view(obj: Any):
    printer(str(obj))
    printer(repr(obj))
    printer(obj)


class ParseTasks:
    """OUTDATED..."""

    def base(self):
        parsed_name()

    def regex(self):
        pattern_namer()

    def error(self):
        show_error()


def parsed_name():
    """OUTDATED???"""
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


#


def pattern_namer():
    """OUTDATED???"""
    namer = NamePattern("{date}_{topic}_sstcore.{suffix}")

    printer(namer)

    name_1: dict[str, str] = {
        "date": f"{day_count()}",
        "topic": "arboreal",
        "suffix": "md",
    }
    forward: str = namer.format(name_1)
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
    """OUTDATED???"""
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
