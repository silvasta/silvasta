"""
Provide typed Data Transfer Objects for the EventBus

- EventDTO: Base for LogDTO and CliDTO

"""


class EventDTO:
    """Give the objects of different Pipelines a uniform root"""

    def __str__(self) -> str:
        return type(self).__name__

    # TODO: check if this dataclass thing here is needed
    def __post_init__(self):
        self._validate()

    def _validate(self):
        pass
