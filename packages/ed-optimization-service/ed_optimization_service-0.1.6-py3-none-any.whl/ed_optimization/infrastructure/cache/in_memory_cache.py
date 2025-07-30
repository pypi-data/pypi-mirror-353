from typing import TypeVar

from ed_optimization.application.contracts.infrastructure.cache.abc_cache import \
    ABCCache
from ed_optimization.application.features.order.dtos import CreateOrderDto

T = TypeVar("T")


class InMemoryCache(ABCCache[list[CreateOrderDto]]):
    def __init__(self) -> None:
        self._cache: dict[str, list[CreateOrderDto]] = {}

    def get(self, key: str) -> list[CreateOrderDto] | None:
        return self._cache.get(key)

    def set(self, key: str, value: list[CreateOrderDto]) -> None:
        self._cache[key] = value
