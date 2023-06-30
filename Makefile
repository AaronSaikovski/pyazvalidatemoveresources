.ONESHELL:

.DEFAULT_GOAL := create

# Set Project Variables
PROJECT_PYTHON_VER = ">=3.11,<3.13"
PROJECT_NAME = "pyazvalidatemoveresources"
PROJECT_DESC = "Azure resource move validation Python script"
PROJECT_AUTHOR = "Aaron Saikovski <asaikovski@outlook.com>"
PROJECT_VERSION = "3.0.3"
PROJECT_LICENSE ="MIT"

## help - Display help about make targets for this Makefile
help:
	@cat Makefile | grep '^## ' --color=never | cut -c4- | sed -e "`printf 's/ - /\t- /;'`" | column -s "`printf '\t'`" -t

## create - Inits the poetry virtual environment and install baseline packages
create: 
	poetry config virtualenvs.in-project true
	poetry init --name=$(PROJECT_NAME) --description=$(PROJECT_DESC) --author=$(PROJECT_AUTHOR) --python=$(PROJECT_PYTHON_VER) --license=$(PROJECT_LICENSE) --no-interaction 
	poetry update
	poetry add --dev pytest pytest-cov black ruff ruff bandit safety pyinstaller
	poetry add azure-common azure-core azure-identity azure-mgmt-core azure-mgmt-resource msal requests types-requests types-urllib3 typing_extensions

## deps - Install the dependencies 
deps: create
	poetry add --dev pytest pytest-cov black ruff ruff bandit safety pyinstaller
	poetry add azure-common azure-core azure-identity azure-mgmt-core azure-mgmt-resource msal requests types-requests types-urllib3 typing_extensions

## activate - Activates the virtual environment
activate: 
	. ./.venv/bin/activate


## install - installs the poetry environment with dependencies
install: 
	poetry install

## run - Run the script main.py
run:  
	poetry run python main.py

## clean - Cleans the environment, Overwrites the pyproject.toml file
clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	rm -rf .venv
	rm -rf venv
	rm -rf .pytest_cache
	rm -rf ./dist
	rm -rf ./build
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf poetry.lock
	cat pyproject_base.toml > pyproject.toml

## test - Tests the project
test: activate
	poetry run python -m pytest tests

## lint - Lints the project using ruff --fix
lint: activate
	poetry run ruff . --fix

## installer - uses pyinstaller to package your Python application into a single package
installer: activate
	pyinstaller ./main.py

.PHONY: help run clean test lint installer deps install