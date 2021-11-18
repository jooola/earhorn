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
	# poetry run pylint earhorn tests
	poetry run pylint earhorn
	# poetry run mypy earhorn tests || true
	poetry run mypy earhorn || true

test: install
	# poetry run pytest -n $(CPU_CORES) --color=yes -v --cov=earhorn tests

ci-publish:
	poetry publish --no-interaction --build
