import json
from typing import Any

from sstcore.events.protocol import LogSerializable

# NEXT:


def serialize_to_ndjson(record: dict[str, Any]) -> str:
    extra = record.get("extra", {})
    raw_obj = extra.pop("raw_obj", None)

    payload = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record.get("message", ""),
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "thread": record.get("thread", {}).get("id"),
        "process": record.get("process", {}).get("id"),
    }

    # Структурированная часть из DTO
    if isinstance(raw_obj, LogSerializable):
        try:
            dto = raw_obj.__log__()
            payload.update(
                {
                    "log_dto": {
                        "message": dto.message,
                        "level": dto.level,
                        "metrics": dto.metrics,
                        "extra": dto.extra,
                    }
                }
            )
        except Exception as e:
            payload["log_dto_error"] = str(e)

    # Остальные поля extra (плоские)
    for k, v in extra.items():
        if isinstance(v, (str, int, float, bool, type(None))):
            payload[k] = v
        elif isinstance(v, (list, dict)):
            # Опционально: усекать или пропускать сложные структуры
            pass

    return json.dumps(payload, ensure_ascii=False) + "\n"
