from contextlib import suppress
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from sstcore.utils import PatternNamer, day_count, printer
from sstcore.utils.parse import ParsedName, StyledName


def main():  # IDEA: google.Fire for dispatching like this?
    printer.title("Start of name_parsing")
    # pattern_namer()
    parsed_name()
    # predefined_keys()
    # styled_name()
    # show_error()
    parsed_basemodel_name()


def parsed_basemodel_name():
    printer.title("Start of parsed_basemodel_name")

    class TreeInfoSchema(BaseModel):
        sprout_id: int
        topic: str

    # Instantiate with the generic type and schema class
    tree_parser: ParsedName[TreeInfoSchema] = ParsedName[TreeInfoSchema](
        pattern="t_{sprout_id}_{topic}",
        schema=TreeInfoSchema,
        strip_extension=True,  # Safely handles Path("t_42_math.json")
    )

    # Backwards parsing returns the BaseModel directly!
    tree_data = tree_parser(Path("t_42_math.json"))

    printer(tree_data)

    print(tree_data.sprout_id)  # 42 (as int)
    print(tree_data.topic)  # "math"

    printer(tree_parser)


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


def styled_name():

    sstfile_dates: StyledName = StyledName.parse_style(
        style_pattern="[{style1}]{name}[/]: [{style2}]{first_tracked}[/] - [{style3}]{last_updated}[/]",
        keys=["name", "first_tracked", "last_updated"],
        styles=["blue", "red", "white"],
    )

    print(sstfile_dates)
    print(sstfile_dates.styled(["file.pdf", datetime.now(), "22-03-2026"]))
    printer(sstfile_dates.styled(["file.pdf", datetime.now(), "22-03-2026"]))


def pattern_namer():
    namer = PatternNamer("{date}_{topic}_sstcore.{suffix}")

    print(namer)

    name_1: dict[str, str] = {
        "date": f"{day_count()}",
        "topic": "arboreal",
        "suffix": "md",
    }
    forward: str = namer.format(**name_1)
    print(forward)

    backward: dict[str, str] = namer.extract(forward)
    print(backward)

    random_fine: dict[str, str] = namer.extract("9598_code_sstcore.py")
    print(random_fine)

    with suppress(ValueError):
        random_bad: dict[str, str] = namer.extract("9_code_stcore.py")
        print(random_bad)

    random_1: dict[str, str] = namer.extract("93-59_sstcore_sstcore.p")
    print(random_1)


if __name__ == "__main__":
    main()
