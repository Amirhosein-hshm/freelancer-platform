import pytest

from app.application.shared.use_case import UseCase


class FakeUseCase(UseCase[int, str]):
    def execute(self, request: int) -> str:
        return str(request)


class TestUseCaseBase:
    def test_concrete_use_case_executes(self):
        assert FakeUseCase().execute(42) == "42"

    def test_use_case_is_abstract(self):
        with pytest.raises(TypeError):
            UseCase()  # type: ignore[abstract]
