.PHONY: install install-dev test lint format typecheck check clean run graph

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-graph:
	pip install -e ".[graph]"

test:
	pytest tests/ -v

lint:
	ruff check odb_read/ tests/

format:
	ruff format odb_read/ tests/

typecheck:
	mypy odb_read/ --ignore-missing-imports

check: lint typecheck test

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
