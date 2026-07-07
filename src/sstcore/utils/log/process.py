"""
Handle CLI Event

- call printer.format

"""
# IDEA: move to __init__?? could stay as well,
# idea was together with __cli__, in cli?

from loguru import logger

from ...events.bus import Event

# NEXT: proper handler


def handle_log_event(event: Event):
    raise NotImplementedError


# IDEA: 1 - regular log string
def smart_log(obj, message=""):
    if hasattr(obj, "__log__"):
        dto = obj.__log__()
        # Route it to loguru with the requested level
        getattr(logger, dto.level)(f"{message} {dto.message}")
    else:
        logger.info(str(obj))


# IDEA: 4 - bind json (maybe move function later on to proper place)
def process_log_event(event):
    target = event.payload.get("target")
    if hasattr(target, "__log__"):
        dto = target.__log__()  # Returns LogDTO
        # Bind the metrics so they appear as top-level JSON keys
        logger.bind(**dto.metrics).log(dto.level.upper(), dto.message)
    else:
        logger.info(str(target))
