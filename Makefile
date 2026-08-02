VENV := .venv/bin

.PHONY: test typecheck lint check install

install:
	$(VENV)/pip install -e ".[dev]"

test:
	$(VENV)/pytest --cov=app.domain --cov=app.application --cov-report=term-missing --cov-fail-under=90

typecheck:
	$(VENV)/mypy src/app/domain src/app/application

lint:
	$(VENV)/ruff check .

check: typecheck lint test
