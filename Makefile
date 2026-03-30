.DEFAULT_GOAL := help

.PHONY: help install lint test check build readme-check clean

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install       Install all dependencies (runtime + build/test)"
	@echo "  lint          Run pylint and flake8"
	@echo "  test          Run pytest (excluding integration tests)"
	@echo "  check         Run lint + test (mirrors CI)"
	@echo "  build         Build the package distribution"
	@echo "  readme-check  Verify README renders correctly on PyPI"
	@echo "  clean         Remove build artifacts and cache files"

install:
	pip install -r requirements-build.txt
	pip install -r requirements.txt

lint:
	build_scripts/run_pylint.sh
	flake8

test:
	pytest --verbose -m "not integration" --timer-top-n 10 --cov-config=.coveragerc --cov

check: lint test

build:
	python -m build

readme-check:
	pip install readme_renderer readme_renderer[md]
	python -m readme_renderer README.md

clean:
	rm -rf .coverage
