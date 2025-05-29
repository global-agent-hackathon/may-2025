.PHONY: all
all: clean fmt check-lint

.PHONY: clean
clean:
	@rm -rf build dist *.egg-info .coverage .coverage.* .eggs .mypy_cache .pytest_cache .ruff_cache
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" | xargs rm -rf

.PHONY: fix-lint
fix-lint:
	@uv run ruff check --fix src tests

.PHONY: fmt
fmt:
	@uv run ruff format src tests

.PHONY: sqlfmt
sqlfmt:
	@uv run sqlfmt src tests

.PHONY: check-lint
check-lint: check-ruff-lint typecheck check-sqlfmt

.PHONY: check-ruff-lint
check-ruff-lint:
	@uv run ruff check src tests

.PHONY: typecheck
typecheck:
	@uv run mypy --install-types --non-interactive src tests

.PHONY: check-sqlfmt
	@uv run sqlfmt --check src tests

.PHONY: pre-commit
pre-commit:
	@uv run pre-commit

.PHONY: pre-commit-all
pre-commit-all:
	@uv run pre-commit run --all-files
