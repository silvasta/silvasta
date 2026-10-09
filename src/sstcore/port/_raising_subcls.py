from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Protocol, reveal_type

# NEXT:
# NEXT:
# NEXT:
# NEXT:


@dataclass(frozen=True)
class TopicConfig:
    prefix: str
    max_retries: int = 3
    dead_letter: bool = True


class ConfiguredEnum(Enum):
    def __init_subclass__(cls, config: TopicConfig, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.config = config


class EventTopics(
    ConfiguredEnum, config=TopicConfig(prefix="events.v1.", dead_letter=False)
):
    USER_CREATED = "user.created"
    USER_DELETED = "user.deleted"


print(EventTopics.config.prefix)
print(EventTopics.USER_CREATED.value)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SubClassBase(Enum):
    def __init_subclass__(cls, config: TopicConfig, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.config = config


# FAIL: # Dynamically spawn a subclass:
# DynamicTopic = SubClassBase(
#     "DynamicTopic",
#     ["PING", "PONG"],
#     config=TopicConfig(prefix="internal."),  # Forwarded to __init_subclass__)
# print(DynamicTopic.config.prefix)  # 'internal.'
# print(DynamicTopic.PING)  # <DynamicTopic.PING: 1>


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class TopicConfig:
    prefix: str
    max_retries: int = 3


class ConfiguredEnum(Enum):
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


reveal_type(Endpoint.USERS.meta.path)


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
class NextSubClassBase(Enum):
    config: ClassVar[object]  # Generic or broad baseline

    def __init_subclass__(cls, config: object, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.config = config


# --- Concrete Enum Subclass ---
class QueueEnum(
    NextSubClassBase, config=RabbitDTO("app.", "orders.#", "amq.direct")
):
    # Subclass narrows the type locally (can be a Protocol or a Child DTO)
    config: ClassVar[HasRouting]

    ORDERS = "orders"


reveal_type(QueueEnum.config)
print(QueueEnum.config.routing_key)


class NextQueueEnum(
    NextSubClassBase, config=RabbitDTO("app.", "orders.#", "amq.direct")
):
    config: ClassVar[RabbitDTO]

    ORDERS = "orders"


reveal_type(NextQueueEnum.config)
print(NextQueueEnum.config.exchange)
