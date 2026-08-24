"""
Prepare Formatter for Emitted Events

- Format colored string with parameter
- Serialize LogDTO to JSON-Line
                                                       DependencyLevel[0]
"""

__all__: list[str] = [
    "load_format_pattern",
    "ndjson_formatter",
]

import json
from typing import Any

from ...port.event.dto import LogDTO
from ...port.view import LogSerializable


def log_dto_to_dict(dto: LogDTO) -> dict[str, Any]:
    """Refactor LogDTO into it's strigly components"""
    return {
        "message": dto.message,
        "level": dto.level.upper(),
        **dto.metrics,
        **dto.extra,
    }


def load_format_pattern() -> str:
    """Compose format template for console and default logs"""

    time = "<green>{time:HH:mm:ss}</green>"
    level = "<level>{level: <8}</level>"
    name = "<cyan>{name}</cyan>"
    func = " <cyan>{function}</cyan>"
    message = "<level>{message}</level>"

    return f"{time} | {level} | {name}:{func} - {message}"


def ndjson_formatter(record) -> str:
    """
    Format event to make it serializable for loguru

    - Return template token pointing to an injected extra field
      (bypass loguru template placeholder engine issues with raw JSON braces)
    """

    payload: dict[str, Any] = {
        "time": record["time"].isoformat(),
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
            payload.update(log_dto_to_dict(dto))
        except Exception as error:
            payload["serialization_error"] = str(error)

    for k, v in extra.items():
        if isinstance(v, (str, int, float, bool, type(None))):
            payload[k] = v

        elif isinstance(v, (list, dict)):
            payload[k] = v  # LATER: start here if lines went to long

    # inject the serialized string into the record's extra namespace
    record["extra"]["raw_ndjson"] = json.dumps(payload, ensure_ascii=False)

    return "{extra[raw_ndjson]}\n"
