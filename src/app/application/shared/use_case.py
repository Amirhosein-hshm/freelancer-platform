from abc import ABC, abstractmethod


class UseCase[TRequest, TResponse](ABC):
    @abstractmethod
    def execute(self, request: TRequest) -> TResponse: ...
