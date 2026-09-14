import pytest

from app.application.shared.use_case import UseCase


class FakeUseCase(UseCase[int, str]):
    async def execute(self, request: int) -> str:
        return str(request)


class TestUseCaseBase:
    async def test_concrete_use_case_executes(self):
        assert await FakeUseCase().execute(42) == "42"

    async def test_use_case_is_abstract(self):
        with pytest.raises(TypeError):
            UseCase()  # type: ignore[abstract]
