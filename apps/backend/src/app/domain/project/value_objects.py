import re
from dataclasses import dataclass
from decimal import Decimal

from app.domain.project.enums import BudgetType
from app.domain.project.exceptions import InvalidBudgetError, InvalidProjectCodeError

_PROJECT_CODE_PATTERN = re.compile(r"^PRJ-\d{4}-\d{3,}$")


@dataclass(frozen=True)
class Budget:
    budget_type: BudgetType
    fixed_amount: Decimal | None
    min_amount: Decimal | None
    max_amount: Decimal | None
    currency_code: str

    def __post_init__(self) -> None:
        if self.budget_type == BudgetType.FIXED:
            if self.fixed_amount is None:
                raise InvalidBudgetError("A FIXED budget requires fixed_amount.")
        elif self.budget_type == BudgetType.RANGE:
            if self.min_amount is None or self.max_amount is None:
                raise InvalidBudgetError("A RANGE budget requires min_amount and max_amount.")
            if self.min_amount > self.max_amount:
                raise InvalidBudgetError("min_amount cannot exceed max_amount.")
        if not self.currency_code.strip():
            raise InvalidBudgetError("currency_code is required.")


@dataclass(frozen=True)
class ProjectCode:
    value: str

    def __post_init__(self) -> None:
        if not _PROJECT_CODE_PATTERN.fullmatch(self.value):
            raise InvalidProjectCodeError(f"Invalid project code '{self.value}'; expected format PRJ-YYYY-NNN.")
