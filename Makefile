.PHONY: test test_verbose run_dev
test:
	poetry run isort . --check
	poetry run ruff check .
	# poetry run python -m pytest
	poetry run mypy --check .

test_verbose:
	poetry run isort . --check --diff
	poetry run ruff check .
	# poetry run python -m pytest -vvv
	poetry run mypy --check .

