from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")


class UseCase(Generic[TRequest, TResponse], ABC):
    @abstractmethod
    async def execute(self, request: TRequest) -> TResponse: ...
