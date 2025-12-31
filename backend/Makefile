.PHONY: install install-local install-wheel run clean lint format type-check security-check help

# Detect OS and set platform-specific variables
VENV := .venv

ifeq ($(OS),Windows_NT)
    PYTHON := py -3
    VENV_PY := $(VENV)/Scripts/python.exe
else
    PYTHON := python3
    VENV_PY := $(VENV)/bin/python
endif

# Default target
help:
	@echo "Available commands:"
	@echo "  install                                   - Create virtual environment and install dependencies"
	@echo "  install-local SDK_PATH=/path/to/sdk       - Install with local SDK for development"
	@echo "  install-wheel WHEEL_PATH=/path/to/wheel   - Install with pre-built wheel for testing"
	@echo "  run                                       - Start the FastAPI server"
	@echo "  clean                                     - Remove virtual environment"
	@echo "  lint                                      - Run flake8 linter"
	@echo "  format                                    - Auto-format code with black and isort"
	@echo "  type-check                                - Run mypy type checking"
	@echo "  security-check                            - Run security vulnerability checks"
	@echo "  help                                      - Show this help message"

# Create virtual environment and install dependencies
install:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Upgrading pip..."
	$(VENV_PY) -m pip install --upgrade pip
	@echo "Installing dependencies..."
	$(VENV_PY) -m pip install -e ".[dev]"
	@echo ""
	@echo "✅ Setup complete!"

# Install a local SDK for testing (meant for internal Wristband development only!)
install-local:
ifndef SDK_PATH
	$(error SDK_PATH is not set. Usage: make install-local SDK_PATH=/path/to/your/wristband-sdk)
endif
	@echo "Installing local SDK in editable mode from $(SDK_PATH)..."
	$(VENV_PY) -m pip install -e $(SDK_PATH) --force-reinstall
	@echo ""
	@echo "✅ Installation complete for LOCAL SDK from $(SDK_PATH)!"

# Install a local SDK wheel for testing (meant for internal Wristband development only!)
install-wheel:
ifndef WHEEL_PATH
	$(error WHEEL_PATH is not set. Usage: make install-wheel WHEEL_PATH=/path/to/your/wheel.whl)
endif
	@echo "Installing SDK wheel from $(WHEEL_PATH)..."
	$(VENV_PY) -m pip install $(WHEEL_PATH) --force-reinstall
	@echo ""
	@echo "✅ Installation complete for WHEEL from $(WHEEL_PATH)!"

# Start development server
run:
	@echo "Starting FastAPI development server..."
	$(VENV_PY) main.py

# Clean up virtual environment by removing the following:
#   - .venv/           Virtual environment directory
#   - build/           Build artifacts from setuptools
#   - dist/            Distribution packages (wheels, sdist)
#   - htmlcov/         HTML coverage reports
#   - .pytest_cache/   Pytest cache directory
#   - .mypy_cache/     Mypy type checker cache
#   - .coverage        Coverage data file
#   - *.egg-info/      Package metadata directories
#   - __pycache__/     Python bytecode cache directories (recursively)
#   - *.pyc            Compiled Python bytecode files (recursively)
clean:
	@echo "Cleaning up virtual environment..."
	@$(PYTHON) -c "import shutil, pathlib; \
		dirs = ['.venv', 'build', 'dist', 'htmlcov', '.pytest_cache', '.mypy_cache']; \
		[shutil.rmtree(p, ignore_errors=True) for p in dirs]; \
		[p.unlink(missing_ok=True) for p in [pathlib.Path('.coverage')]]; \
		[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]; \
		[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; \
		[p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]"
	@echo "✅ Cleanup complete."

# Code Quality
lint:
	@echo "Running flake8 linter..."
	$(VENV_PY) -m flake8 src
	@echo "✅ Linting complete!"

format:
	@echo "Formatting code with isort and black..."
	$(VENV_PY) -m isort src
	$(VENV_PY) -m black src
	@echo "✅ Code formatting complete!"

type-check:
	@echo "Running mypy type checking..."
	$(VENV_PY) -m mypy src
	@echo "✅ Type checking complete!"

# Security checks
security-check:
	@echo "🔍 Checking dependencies for known vulnerabilities..."
	$(VENV_PY) -m pip_audit
	@echo ""
	@echo "🔍 Scanning source code for security issues..."
	$(VENV_PY) -m bandit -r src
	@echo ""
	@echo "✅ Security checks complete!"
