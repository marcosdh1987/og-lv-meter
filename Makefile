SHELL=/bin/bash
PATH := .venv/bin:$(PATH)
PYTHON_VERSION = 3.7
export ENV=dev

install:
	@( \
		if ! command -v pyenv &> /dev/null; then \
			echo "pyenv is not installed. Please install pyenv first."; \
			exit 1; \
		fi; \
		if ! pyenv versions --bare | grep -q "^$(PYTHON_VERSION)$$"; then \
			echo "Python $(PYTHON_VERSION) is not installed via pyenv. Installing..."; \
			pyenv install $(PYTHON_VERSION); \
		fi; \
		PYENV_VERSION=$(PYTHON_VERSION) pyenv exec python -m venv --copies .venv; \
		source .venv/bin/activate; \
		pip install -qU pip; \
		pip install -r requirements.in; \
	)

autoflake:
	@autoflake . --check --recursive --remove-all-unused-imports --remove-unused-variables --exclude .venv;

black:
	@black . --check --exclude '.venv|build|target|dist|.cache|node_modules';

isort:
	@isort . --check-only;

lint: black isort autoflake

lint-fix:
	@black . --exclude '.venv|build|target|dist';
	@isort .;
	@autoflake . --in-place --recursive --exclude .venv --remove-all-unused-imports --remove-unused-variables;

docs:
	@if [ ! -f ./docs/make.bat ]; then (cd docs && sphinx-quickstart); fi;
	@(cd docs && make html);
	@if command -v open; then open ./docs/*build/html/index.html; fi;


#create a test rtu device
create-rtu:
	@docker run --name modbus-server -p 5020:5020 -d oitc/modbus-server
