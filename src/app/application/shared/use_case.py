from abc import ABC, abstractmethod


class UseCase[TRequest, TResponse](ABC):
    @abstractmethod
    async def execute(self, request: TRequest) -> TResponse: ...
