from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Protocol, reveal_type


@dataclass(frozen=True)
class TopicConfig:
    prefix: str
    max_retries: int = 3
    dead_letter: bool = True


class ConfiguredEnum(Enum):
    def __init_subclass__(cls, config: TopicConfig, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.config = config


# Pass the DTO instance directly in the class signature:
class EventTopics(
    ConfiguredEnum, config=TopicConfig(prefix="events.v1.", dead_letter=False)
):
    USER_CREATED = "user.created"
    USER_DELETED = "user.deleted"


print(EventTopics.config.prefix)  # 'events.v1.'
print(EventTopics.USER_CREATED.value)  # 'user.created'


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class BaseEnum(Enum):
    def __init_subclass__(cls, config: TopicConfig, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.config = config


# Dynamically spawn a subclass
DynamicTopic = BaseEnum(
    "DynamicTopic",
    ["PING", "PONG"],
    config=TopicConfig(prefix="internal."),  # Forwarded to __init_subclass__
)

print(DynamicTopic.config.prefix)  # 'internal.'
print(DynamicTopic.PING)  # <DynamicTopic.PING: 1>


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class TopicConfig:
    prefix: str
    max_retries: int = 3


class ConfiguredEnum(Enum):
    # Annotate on the base class so type checkers know it exists
    config: ClassVar[TopicConfig]

    def __init_subclass__(cls, config: TopicConfig, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.config = config


class EventTopics(
    ConfiguredEnum, config=TopicConfig(prefix="events.v1.", max_retries=5)
):
    USER_CREATED = "user.created"


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class EndpointMeta:
    path: str
    rate_limit: int


class Endpoint(Enum):
    _value_: EndpointMeta

    @property
    def meta(self) -> EndpointMeta:
        return self.value

    USERS = EndpointMeta("/users", 100)
    ORDERS = EndpointMeta("/orders", 50)


# Type checkers know `meta` has .path and .rate_limit:
reveal_type(Endpoint.USERS.meta.path)  # Revealed type: "str"


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# --- Protocols / DTOs ---
class HasRouting(Protocol):
    prefix: str
    routing_key: str


@dataclass(frozen=True)
class RabbitDTO:
    prefix: str
    routing_key: str
    exchange: str


# --- Base Enum ---
class BaseEnum(Enum):
    config: ClassVar[object]  # Generic or broad baseline

    def __init_subclass__(cls, config: object, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.config = config


# --- Concrete Enum Subclass ---
class QueueEnum(BaseEnum, config=RabbitDTO("app.", "orders.#", "amq.direct")):
    # Subclass narrows the type locally (can be a Protocol or a Child DTO)
    config: ClassVar[HasRouting]

    ORDERS = "orders"


# Type checker narrows the type:
reveal_type(QueueEnum.config)  # Revealed type: HasRouting
print(QueueEnum.config.routing_key)
