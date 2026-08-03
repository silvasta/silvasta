"""
Provide typed Data Transfer Objects for the EventBus

- EventDTO: Base for LogDTO and CliDTO

"""


class EventDTO:
    """Give the objects of different Pipelines a uniform root"""

    def __str__(self) -> str:
        return type(self).__name__

    # FIX: dataclass? check kw_only
    def __post_init__(self):
        self._validate()

    def _validate(self):
        pass
