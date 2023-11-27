.PHONY: all setup check-update lint build test clean

all: clean setup

setup:
	poetry config --local virtualenvs.in-project true
	poetry install
	poetry run pre-commit install

check-update:
	poetry show --outdated
	poetry update --dry-run

build:
	poetry build

lint:
	poetry run pre-commit run --all-files

test:
	poetry run tox

clean:
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .mypy_cache
	rm -rf .tox
	rm -rf .pytest_cache
	rm -rf poetry.lock
	rm -rf .readthedocs.yml
	rm -rf .venv
