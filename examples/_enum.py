from enum import Enum, auto

from sstcore.port.structures._enum import SstEnumMeta
from sstcore.port.structures._enumfield import EnumField


class SstEnum(Enum, metaclass=SstEnumMeta):
    """Base Enum with zero-indexing, resolution, and EnumField registry."""


class Severity(SstEnum, zero=True):
    INFO = auto()
    WARN = auto()
    ERROR = auto()

    # Bound via deferred decorator (e.g., from another module)
    badge = EnumField()
    # Partial table with a fallback default
    exit_code = EnumField.lazy(
        lambda: {Severity.ERROR: 1},
        default=0,
    )


@Severity.badge.bind_loader
def _load_badges() -> dict[Severity, str]:
    return {
        Severity.INFO: "[i]",
        Severity.WARN: "[!]",
        Severity.ERROR: "[x]",
    }


class Color(SstEnum):
    RED = auto()
    GREEN = auto()

    hex_code = EnumField.lazy(
        lambda: {Color.RED: "#ff0000", Color.GREEN: "#00ff00"}
    )


# Nothing hydrated yet
assert not Severity.fields_ready()
assert not Color.fields_ready()

# Single global validation hook (ideal for a pytest test)
# Passes: badge & hex_code are complete; exit_code has default=0 fallback
SstEnumMeta.validate_all_registered(strict=False)

assert Severity.fields_ready()
assert Color.fields_ready()
assert Severity.WARN.badge == "[!]"
assert Severity.INFO.exit_code == 0
assert Color.hex_code["RED"] == "#ff0000"

# strict=True enforces 1-to-1 table coverage even when fallbacks exist
try:
    SstEnumMeta.validate_all_registered(strict=True)
except KeyError as err:
    print(err)
    # Severity.exit_code: Missing value(s) for Enum Member(s): INFO, WARN
