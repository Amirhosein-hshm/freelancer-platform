from dataclasses import FrozenInstanceError, dataclass

import pytest

from app.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class Money(ValueObject):
    amount: int
    currency: str


class TestValueObject:
    def test_equality_is_based_on_all_fields(self):
        assert Money(100, "USD") == Money(100, "USD")

    def test_inequality_when_any_field_differs(self):
        assert Money(100, "USD") != Money(200, "USD")
        assert Money(100, "USD") != Money(100, "EUR")

    def test_value_object_is_hashable_and_frozen(self):
        value = Money(100, "USD")
        assert {value, Money(100, "USD")} == {value}
        with pytest.raises(FrozenInstanceError):
            value.amount = 999
