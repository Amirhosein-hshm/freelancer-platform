import re
from dataclasses import dataclass

from app.domain.iam.exceptions import InvalidEmailError, InvalidPhoneNumberError
from app.domain.shared.value_object import ValueObject

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\s\-()]{6,19}$")


@dataclass(frozen=True)
class Email(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_PATTERN.match(self.value):
            raise InvalidEmailError(f"Invalid email address: {self.value!r}.")


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    value: str

    def __post_init__(self) -> None:
        if not _PHONE_PATTERN.match(self.value):
            raise InvalidPhoneNumberError(f"Invalid phone number: {self.value!r}.")


@dataclass(frozen=True)
class PasswordHash(ValueObject):
    """Wrapper around a hashed password.

    The entity never sees a plain-text password; hashing is performed in the
    application layer through ``IPasswordHasher``.
    """

    value: str
