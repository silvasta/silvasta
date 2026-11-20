import pickle

import pytest
from loguru import logger

from sstcore.port._error import SstError, SstPortError
from sstcore.port.primitives import Args, Kwargs, Params, Var

# --- 1. SstError Init Cases ---


def test_sst_error_cases():
    # Empty
    e_empty = SstError()
    assert str(e_empty) == ""
    assert not e_empty.params.args and not e_empty.params.kwargs

    # Message only (optimal path)
    e_msg = SstError("connection failed")
    assert str(e_msg) == "connection failed"
    assert e_msg.args == ("connection failed",)

    # Message + extra args & kwargs
    e_full = SstError("timeout", 30, host="localhost")
    assert "timeout" in str(e_full)
    assert e_full.params["host"] == "localhost"

    # Kwargs only (no message)
    e_kw = SstError(code=503, retry=True)
    assert "code=503" in str(e_kw)
    assert e_kw.params["retry"] is True


# --- 2. BaseControl NamedTuple Pickling ---


@pytest.mark.parametrize(
    "obj",
    [
        Var("port", 8080),
        Args.absorb("a", 1, (2, 3)),
        Kwargs.absorb(host="localhost", debug=True),
        Params.absorb("start", 42, color="green"),
    ],
)
def test_control_namedtuples_pickle_roundtrip(obj):
    restored = pickle.loads(pickle.dumps(obj))
    assert type(restored) is type(obj)
    assert restored == obj
    assert str(restored) == str(obj)


# --- 3. SstError.weave & Subclass Pickling ---


class CustomPortError(SstPortError):
    def __init__(self, port: int, *args, **kwargs):
        self.port = port
        super().__init__(*args, **kwargs)


def test_woven_error_pickle_preserves_state():
    WovenErr = CustomPortError.weave(ConnectionError, prefix="Net")  # noqa:N806
    err = WovenErr(5432, "refused", host="127.0.0.1")

    assert isinstance(err, CustomPortError)
    assert isinstance(err, ConnectionError)

    restored = pickle.loads(pickle.dumps(err))

    assert type(restored) is WovenErr  # Hits @cache, same class object
    assert restored.port == 5432
    assert restored.params["host"] == "127.0.0.1"
    assert str(restored) == str(err)


# --- 4. Loguru enqueue=True Integration ---


def test_loguru_enqueued_woven_error():
    captured: list[str] = []
    handler_id = logger.add(captured.append, enqueue=True, format="{message}")

    WovenErr = CustomPortError.weave(ValueError, prefix="Log")  # noqa:N806
    try:
        try:
            raise WovenErr(8080, "bad payload", payload_size=1024)
        except WovenErr:
            logger.exception("caught woven error")
        logger.complete()  # Flushes background queue
    finally:
        logger.remove(handler_id)

    output = "".join(captured)
    assert "caught woven error" in output
    assert "bad payload" in output
