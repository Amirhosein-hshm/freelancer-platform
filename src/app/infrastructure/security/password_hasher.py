from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.application.shared.ports import IPasswordHasher


class Argon2PasswordHasher(IPasswordHasher):
    """Argon2id password hashing via ``argon2-cffi`` (library defaults).

    Hashing runs in a worker thread so the event loop is never blocked.
    """

    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    async def hash(self, plain_password: str) -> str:
        from asyncio import to_thread

        return await to_thread(self._hasher.hash, plain_password)

    async def verify(self, plain_password: str, hashed: str) -> bool:
        from asyncio import to_thread

        try:
            return await to_thread(self._hasher.verify, hashed, plain_password)
        except VerifyMismatchError:
            return False
