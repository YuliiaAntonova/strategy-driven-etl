.PHONY: help venv install lint lint-strict format

PY := .venv/bin/python
PIP := .venv/bin/pip

help:
	@echo "Targets:"
	@echo "  venv     - create local virtualenv in .venv"
	@echo "  install  - install project deps into .venv"
	@echo "  lint     - run pylint using .venv interpreter (avoids E0401)"
	@echo "  format   - (optional) run black if installed"

venv:
	python3 -m venv .venv

install: venv
	$(PIP) install -U pip
	$(PIP) install -e .
	$(PIP) install pylint

lint:
	$(PY) -m pylint --exit-zero src

lint-strict:
	$(PY) -m pylint src

format:
	$(PY) -m black src

