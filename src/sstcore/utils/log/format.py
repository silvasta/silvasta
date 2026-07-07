"""
Prepare Formatter for emited Events

- Concat colored string with parameter
- Serialize LogDTO to 1 line JSON
"""

import json
from typing import Any

from ...events.dto import LogDTO
from ...events.protocol import LogSerializable


def load_format_pattern() -> str:
    """Compose format template for console and default logs"""

    time = "<green>{time:HH:mm:ss}</green>"
    level = "<level>{level: <8}</level>"
    name = "<cyan>{name}</cyan>"
    func = " <cyan>{function}</cyan>"
    msg = "<level>{message}</level>"

    return f"{time} | {level} | {name}:{func} - {msg}"


def ndjson_formatter(record) -> str:
    """Format event to make it serializable for loguru"""

    payload: dict[str, Any] = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record.get("message", ""),
        "module": record.get("name"),
        "function": record.get("function"),
        "line": record.get("line"),
    }

    extra: dict[str, Any] = record.get("extra", {})
    raw_obj: Any = extra.pop("raw_obj", None)

    if isinstance(raw_obj, LogSerializable):
        try:
            dto: LogDTO = raw_obj.__log__()
            payload.update(dto.to_dict())
        except Exception as err:
            payload["serialization_error"] = str(err)

    for k, v in extra.items():
        if isinstance(v, (str, int, float, bool, type(None))):
            payload[k] = v

        elif isinstance(v, (list, dict)):  # LATER: here if lines went to long
            payload[k] = v

    return json.dumps(payload, ensure_ascii=False) + "\n"
