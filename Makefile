.PHONY: install format lint test

SHELL = bash
CPU_CORES = $(shell nproc)

all: install format lint test

install-poetry:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python3 -

INSTALL_STAMP := .installed
install: $(INSTALL_STAMP)
$(INSTALL_STAMP):
	poetry install
	touch $(INSTALL_STAMP)

format: install
	poetry run black .
	poetry run isort . --profile black

lint: install
	poetry run black . --diff --check
	poetry run isort . --profile black --check
	poetry run pylint --jobs=$(CPU_CORES) earhorn tests
	poetry run mypy earhorn tests || true

test: install
	poetry run pytest -n $(CPU_CORES) --color=yes -v --cov=earhorn tests

release: lint test
	./scripts/release.sh

ci-publish:
	poetry publish --no-interaction --build

changelog:
	git-chglog --output CHANGELOG.md
	pre-commit run prettier --all || true
