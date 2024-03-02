.PHONY: install format lint test

SHELL = bash
CPU_CORES = $$(( $(shell nproc) > 4 ? 4 : $(shell nproc) ))

all: install format lint test

install-poetry:
	curl -sSL https://install.python-poetry.org | python3 -

export POETRY_VIRTUALENVS_IN_PROJECT = true

install: .venv
.venv:
	poetry install --all-extras

format: .venv
	poetry run black .
	poetry run isort .

lint: .venv
	poetry run black . --diff --check
	poetry run isort . --check
	poetry run pylint --jobs=$(CPU_CORES) earhorn tests
	poetry run mypy earhorn tests || true

test: .venv
	poetry run pytest -n $(CPU_CORES) --color=yes -v --cov=earhorn tests

ci-publish:
	poetry publish --no-interaction --build
