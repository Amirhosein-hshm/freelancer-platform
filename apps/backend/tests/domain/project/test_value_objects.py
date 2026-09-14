from decimal import Decimal

import pytest

from app.domain.project.enums import BudgetType
from app.domain.project.exceptions import InvalidBudgetError, InvalidProjectCodeError
from app.domain.project.value_objects import Budget, ProjectCode


class TestProjectCode:
    def test_valid_format(self):
        assert ProjectCode("PRJ-2026-001").value == "PRJ-2026-001"

    def test_invalid_format_raises(self):
        for bad in ("PRJ-2026", "PRJ-26-001", "XYZ-2026-001", "prj-2026-001", "PRJ-2026-001x"):
            with pytest.raises(InvalidProjectCodeError):
                ProjectCode(bad)


class TestBudget:
    def test_fixed_requires_amount(self):
        with pytest.raises(InvalidBudgetError):
            Budget(
                budget_type=BudgetType.FIXED,
                fixed_amount=None,
                min_amount=None,
                max_amount=None,
                currency_code="USD",
            )

    def test_fixed_valid(self):
        budget = Budget(
            budget_type=BudgetType.FIXED,
            fixed_amount=Decimal("1000"),
            min_amount=None,
            max_amount=None,
            currency_code="USD",
        )
        assert budget.fixed_amount == Decimal("1000")

    def test_range_requires_bounds(self):
        with pytest.raises(InvalidBudgetError):
            Budget(
                budget_type=BudgetType.RANGE,
                fixed_amount=None,
                min_amount=Decimal("100"),
                max_amount=None,
                currency_code="USD",
            )

    def test_range_min_le_max(self):
        with pytest.raises(InvalidBudgetError):
            Budget(
                budget_type=BudgetType.RANGE,
                fixed_amount=None,
                min_amount=Decimal("500"),
                max_amount=Decimal("100"),
                currency_code="USD",
            )

    def test_range_valid(self):
        budget = Budget(
            budget_type=BudgetType.RANGE,
            fixed_amount=None,
            min_amount=Decimal("100"),
            max_amount=Decimal("500"),
            currency_code="USD",
        )
        assert budget.min_amount == Decimal("100")

    def test_empty_currency_raises(self):
        with pytest.raises(InvalidBudgetError):
            Budget(
                budget_type=BudgetType.NEGOTIABLE,
                fixed_amount=None,
                min_amount=None,
                max_amount=None,
                currency_code="",
            )
