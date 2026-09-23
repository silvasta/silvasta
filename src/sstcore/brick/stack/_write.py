"""
Launch the StubFile Writer and Type the Stackings

uv run -m sstcore.brick.stack._write

"""

import itertools
from collections.abc import Mapping
from pathlib import Path

from ..time import day_count_plus
from . import _test_data as test_data


class Config:
    # DRYRUN = True  # toggle by comment

    @staticmethod
    def dry_run():
        return hasattr(Config, "DRYRUN")

    @staticmethod
    def target_file(stem: str) -> Path:  # LATER: PathGuard
        return stub_file(stem)


def main():
    # write_stub_for_colors()
    # write_stub_for_random()
    pass


#  LINE: -- Writer -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def write_stub_for_colors():
    schema: dict[str, list[str]] = {
        "colors": list(test_data.ANSI_COLORS.keys()),
        "modifiers": list(test_data.ANSI_MODIFIERS.keys()),
    }

    stub_code = generate_fluent_stubs(
        class_prefix="Printer",
        group_mappings=schema,
        call_signature="def __call__(self, text: str) -> str: ...",
    )

    file: Path = Config.target_file("_colors")

    if Config.dry_run():
        print(f"Target StubFile at: {file}")
    else:
        print(f"Write StubFile to: {file}")
        file.write_text(data=stub_code)


def write_stub_for_random():
    schema: dict[str, list[str]] = {
        "attr1": list(test_data.ATTR1.keys()),
        "attr2": list(test_data.ATTR2.keys()),
        "attr3": list(test_data.ATTR3.keys()),
    }

    stub_code = generate_fluent_stubs(
        class_prefix="Greeter",
        group_mappings=schema,
        call_signature="def __call__(self, text: str) -> str: ...",
    )

    file: Path = Config.target_file("_random")

    if Config.dry_run():
        print(f"Target StubFile at: {file}")
    else:
        print(f"Write StubFile to: {file}")
        file.write_text(data=stub_code)


#  LINE: -- Generic -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def _generate_class_name(state: frozenset[str], class_prefix: str) -> str:
    if not state:
        return f"{class_prefix}Empty"  # TODO: better entry point
    return f"{class_prefix}" + "".join(sorted(s.capitalize() for s in state))


def _generate_power_set(groups: list[str]) -> list[frozenset[str]]:
    return [
        frozenset(combo)
        for i in range(len(groups) + 1)
        for combo in itertools.combinations(groups, i)
    ]


def generate_fluent_stubs(  # LATER: use Machine
    class_prefix: str,
    group_mappings: Mapping[str, list[str]],
    call_signature: str = "def __call__(self, text: str) -> str: ...",
) -> str:
    """Generates .pyi stub string for a fluent builder state machine"""

    groups: list[str] = sorted(group_mappings.keys())
    power_set: list[frozenset[str]] = _generate_power_set(groups)

    stub_lines: list[str] = []

    for current_state in power_set:
        class_name = _generate_class_name(current_state, class_prefix)
        stub_lines.append(f"class {class_name}:")

        available_groups: set[str] = set(groups) - current_state
        has_methods = False

        for group in sorted(available_groups):
            next_state: frozenset[str] = current_state | {group}
            next_class_name = _generate_class_name(next_state, class_prefix)

            for attr in group_mappings[group]:
                stub_lines.append("    @property")
                stub_lines.append(
                    f"    def {attr}(self) -> {next_class_name}: ..."
                )
                has_methods = True

        stub_lines.append(f"    {call_signature}")
        if not has_methods:
            stub_lines.append("    pass")

        stub_lines.append("")

    return "\n".join(stub_lines)


#  LINE: -- Paths -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def stub_dir(dir: str = "_stubs") -> Path:
    path: Path = Path(__file__).parent / dir
    path.mkdir(parents=True, exist_ok=True)
    return path


def stub_file(stem: str = "_stub") -> Path:
    file: Path = stub_dir() / f"{stem}.pyi"
    if file.exists():
        backup_stem = f"{file.stem}_{day_count_plus()}"
        print(f"Transering old file: {backup_stem}")
        file.move(target=file.with_stem(backup_stem))
    return file


def local_stub_file() -> Path:  # EXTRACT: to system.config
    return stub_file_from_file(file=Path(__file__))


def local_stub_dir_file() -> Path:  # EXTRACT: to system.config
    return stub_dir_file(file=Path(__file__))


def stub_file_from_file(
    file: Path, extension: str = "_stub"
) -> Path:  # TODO: PathGuard
    # EXTRACT: to system.config
    name = f"{file.stem}{extension}.pyi"
    return file.parent / name


def stub_dir_file(file: Path, dir: str = "_stub") -> Path:  # TODO: PathGuard
    name = f"{file.stem}.pyi"
    return file.parent / dir / name


if __name__ == "__main__":
    main()
