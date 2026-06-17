from sstcore import printer
from sstcore.exceptions import (
    NotImplementedDispatchError,
    NotImplementedMixinError,
    TuiSelectorError,
)


def main():
    """Run all exception UI tests"""
    test_dispatch_error()
    test_mixin_error()
    test_tui_error()


def test_dispatch_error():
    printer.title("Testing: NotImplementedDispatchError")
    try:
        bad_target = complex(1, 2)
        raise NotImplementedDispatchError(
            bad_target, "unexpected_arg", strict=True, mode="fast"
        )
    except NotImplementedDispatchError as error:
        printer(error)


def test_mixin_error():
    printer.title("Testing: NotImplementedMixinError")
    try:
        raise NotImplementedMixinError(
            base="BasePrinter", mixin="ColorMixin", func="_format"
        )
    except NotImplementedMixinError as error:
        printer(error)


def test_tui_error():
    printer.title("Testing: TuiSelectorError")
    try:
        raise TuiSelectorError()
    except TuiSelectorError as error:
        try:
            printer.danger(error)  # FIX: printer
        except NotImplementedDispatchError as error:
            printer(error)


if __name__ == "__main__":
    main()
