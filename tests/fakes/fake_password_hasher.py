from app.application.shared.ports import IPasswordHasher


class FakePasswordHasher(IPasswordHasher):
    """Deterministic, reversible fake — never use a real hash in tests."""

    PREFIX = "fake-hash:"

    def hash(self, plain_password: str) -> str:
        return f"{self.PREFIX}{plain_password}"

    def verify(self, plain_password: str, hashed: str) -> bool:
        return hashed == self.hash(plain_password)
