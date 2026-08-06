"""
Show examples in isolated environment without any deeper purpose

- Platform to test and show Parsed Names and Styles

"""

from contextlib import suppress
from typing import Any

import fire

from sstcore.format.name import NamePattern, ParsedName
from sstcore.utils import day_count, printer
from sstcore.utils.parse import SchemaName

pattern1: str = "{day}_summary.{suffix}"


def main():
    printer.title("Start of name_parsing")
    fire.Fire(ParseTasks)


def view(obj: Any):
    printer(str(obj))
    printer(repr(obj))
    printer(obj)


class ParseTasks:
    """OUTDATED..."""

    def schema(self):
        schema_name()

    def core(self):
        parsed_name()

    # old...
    def parse(self):
        old_parsed_name()

    # old...
    def regex(self):
        pattern_namer()

    # old...
    def error(self):
        show_error()


def parsed_name():
    printer.title("Start of new parsed_name")

    pattern: str = "{day}_summary.{suffix}"
    parser = ParsedName(pattern=pattern)
    printer(parser)
    # TODO: example with DTO return


def schema_name():
    pattern = "t_{id}_{topic}"
    schema = SchemaName(pattern=pattern)

    printer(str(schema))
    printer(schema)
    printer(f"{schema!r}")

    name = "t_33_validation"
    printer(schema(name))

    keys = (11, "test")
    printer(schema(keys))


def old_parsed_name():
    """OUTDATED???"""
    printer.title("Start of old_parsed_name")

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
