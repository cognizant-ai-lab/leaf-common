.DEFAULT_GOAL := help

# Makefile for developer convenience only - not part of build infrastructure
.PHONY: help install lint test check build

help:
	@echo "Makefile for developer convenience only"
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install       Install all dependencies (runtime + build/test)"
	@echo "  lint          Run pylint and flake8"
	@echo "  test          Run pytest (excluding integration tests)"
	@echo "  check         Run lint + test (mirrors CI)"
	@echo "  build         Build the package distribution"

install:
	pip install -r requirements-build.txt
	pip install -r requirements.txt

lint:
	build_scripts/run_pylint.sh
	flake8

test:
	pytest --verbose -m "not integration" --timer-top-n 10 --cov-config=.coveragerc --cov
	rm -rf .coverage

check: lint test

build:
	python -m build
