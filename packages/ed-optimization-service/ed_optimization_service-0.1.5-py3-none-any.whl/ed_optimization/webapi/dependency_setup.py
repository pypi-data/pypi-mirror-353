from typing import Annotated

from ed_domain.persistence.async_repositories.abc_async_unit_of_work import \
    ABCAsyncUnitOfWork
from ed_infrastructure.persistence.sqlalchemy.unit_of_work import UnitOfWork
from fastapi import Depends
from rmediator.mediator import Mediator

from ed_optimization.application.contracts.infrastructure.api.abc_api import \
    ABCApi
from ed_optimization.application.contracts.infrastructure.cache.abc_cache import \
    ABCCache
from ed_optimization.application.contracts.infrastructure.message_queue.abc_rabbitmq_producers import \
    ABCRabbitMQProducers
from ed_optimization.application.features.order.handlers.commands.process_order_command_handler import \
    ProcessOrderCommandHandler
from ed_optimization.application.features.order.requests.commands.process_order_command import \
    ProcessOrderCommand
from ed_optimization.common.generic_helpers import get_config
from ed_optimization.common.typing.config import Config
from ed_optimization.infrastructure.api.api_handler import ApiHandler
from ed_optimization.infrastructure.cache.in_memory_cache import InMemoryCache
from ed_optimization.infrastructure.message_queue.rabbitmq_producers import \
    RabbitMQProducers


def get_cache() -> ABCCache:
    return InMemoryCache()


def get_uow(config: Annotated[Config, Depends(get_config)]) -> ABCAsyncUnitOfWork:
    return UnitOfWork(config["db"])


def get_api(config: Annotated[Config, Depends(get_config)]) -> ABCApi:
    return ApiHandler(config["core_api"])


def get_rabbitmq_producers(
    config: Annotated[Config, Depends(get_config)],
) -> ABCRabbitMQProducers:
    return RabbitMQProducers(config)


def mediator(
    rabbitmq_producers: Annotated[
        ABCRabbitMQProducers, Depends(get_rabbitmq_producers)
    ],
    uow: Annotated[ABCAsyncUnitOfWork, Depends(get_uow)],
    cache: Annotated[ABCCache, Depends(get_cache)],
    api: Annotated[ABCApi, Depends(get_api)],
) -> Mediator:
    mediator = Mediator()

    handlers = [
        (
            ProcessOrderCommand,
            ProcessOrderCommandHandler(uow, rabbitmq_producers, cache, api),
        )
    ]
    for command, handler in handlers:
        mediator.register_handler(command, handler)

    return mediator
