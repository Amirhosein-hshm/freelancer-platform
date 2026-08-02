from app.application.shared.ports import ITicketCodeGenerator


class FakeTicketCodeGenerator(ITicketCodeGenerator):
    def __init__(self, prefix: str = "TCK") -> None:
        self._prefix = prefix
        self._counter = 0

    def next_code(self, year: int) -> str:
        self._counter += 1
        return f"{self._prefix}-{year}-{self._counter:03d}"
