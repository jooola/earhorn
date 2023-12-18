.PHONY: install format lint test

SHELL = bash
CPU_CORES = $$(( $(shell nproc) > 4 ? 4 : $(shell nproc) ))

all: install format lint test

install-poetry:
	curl -sSL https://install.python-poetry.org | python3 -

POETRY_VIRTUALENVS_IN_PROJECT = true

INSTALL_STAMP := .installed
install: $(INSTALL_STAMP)
$(INSTALL_STAMP):
	poetry install --all-extras
	touch $(INSTALL_STAMP)

format: install
	poetry run black .
	poetry run isort . --combine-as --profile black

lint: install
	poetry run black . --diff --check
	poetry run isort . --combine-as --profile black --check
	poetry run pylint --jobs=$(CPU_CORES) earhorn tests
	poetry run mypy earhorn tests || true

test: install
	poetry run pytest -n $(CPU_CORES) --color=yes -v --cov=earhorn tests

release: lint test
	./scripts/release.sh

ci-publish:
	poetry publish --no-interaction --build
