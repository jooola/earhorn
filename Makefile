.PHONY: install format lint test

SHELL = bash
CPU_CORES = $$(( $(shell nproc) > 4 ? 4 : $(shell nproc) ))

all: install format lint test

install: venv
venv:
	python3 -m venv venv
	venv/bin/pip install -e .[dev,s3,sentry]

lint: venv
	venv/bin/pylint --jobs=$(CPU_CORES) earhorn tests
	venv/bin/mypy earhorn tests

test: venv
	venv/bin/pytest -n $(CPU_CORES) --color=yes -v --cov=earhorn tests

clean:
	rm -Rf venv
