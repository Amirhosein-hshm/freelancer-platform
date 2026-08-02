from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject(ABC):  # noqa: B024 - intentionally abstract base, no abstract members
    """Base for immutable value objects; equality is based on all fields."""
