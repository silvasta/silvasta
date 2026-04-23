from contextlib import suppress
from datetime import datetime

from silvasta.config.names import ParsedName, StyledName
from silvasta.utils import day_count, printer
from silvasta.utils.parse import PatternNamer


def main():
    print("Start of name_parsing")
    # pattern_namer()
    # parsed_name()
    # predefined_keys()
    styled_name()


def styled_name():

    sstfile_dates: StyledName = StyledName.parse_style(
        style_pattern="[{style1}]{name}[/]: [{style2}]{first_tracked}[/] - [{style3}]{last_updated}[/]",
        keys=["name", "first_tracked", "last_updated"],
        styles=["blue", "red", "white"],
    )

    print(sstfile_dates)
    print(sstfile_dates.styled(["file.pdf", datetime.now(), "22-03-2026"]))
    printer(sstfile_dates.styled(["file.pdf", datetime.now(), "22-03-2026"]))


def parsed_name():
    pattern: str = "{day}_summary.{suffix}"
    summary_file: ParsedName = ParsedName.only_from_pattern(pattern=pattern)
    print(summary_file)

    # Fine
    print(summary_file({"day": str(day_count()), "suffix": "md"}))
    print(summary_file("9607_summary.md"))

    with suppress(ValueError):
        print(summary_file({"suffix": "md"}))

    print(summary_file("962_summary.md"))

    with suppress(ValueError):
        print(summary_file("962_summary_1.md"))
        print("it works!")


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
