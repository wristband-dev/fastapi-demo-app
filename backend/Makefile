.PHONY: install install-local install-wheel run clean lint format type-check security-check help

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
	python3 -m venv .venv
	@echo "Upgrading pip..."
	.venv/bin/pip install --upgrade pip
	@echo "Installing dependencies..."
	.venv/bin/pip install -e ".[dev]"
	@echo ""
	@echo "✅ Setup complete!"

# Install a local SDK for testing (meant for internal Wristband development only!)
install-local:
ifndef SDK_PATH
	$(error SDK_PATH is not set. Usage: make install-local SDK_PATH=/path/to/your/wristband-sdk)
endif
	@echo "Installing local SDK in editable mode from $(SDK_PATH)..."
	.venv/bin/pip install -e $(SDK_PATH) --force-reinstall
	@echo ""
	@echo "✅ Installation complete for LOCAL SDK from $(SDK_PATH)!"

install-wheel:
ifndef WHEEL_PATH
	$(error WHEEL_PATH is not set. Usage: make install-wheel WHEEL_PATH=/path/to/your/wheel.whl)
endif
	@echo "Installing SDK wheel from $(WHEEL_PATH)..."
	.venv/bin/pip install $(WHEEL_PATH) --force-reinstall
	@echo ""
	@echo "✅ Installation complete for WHEEL from $(WHEEL_PATH)!"

# Start development server
run:
	@echo "Starting FastAPI development server..."
	.venv/bin/python main.py

# Clean up virtual environment
clean:
	@echo "Cleaning up virtual environment..."
	rm -rf .venv/ build/ dist/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleanup complete."

# Code Quality
lint:
	@echo "Running flake8 linter..."
	.venv/bin/python -m flake8 src
	@echo "✅ Linting complete!"

format:
	@echo "Formatting code with isort and black..."
	.venv/bin/python -m isort src
	.venv/bin/python -m black src
	@echo "✅ Code formatting complete!"

type-check:
	@echo "Running mypy type checking..."
	.venv/bin/python -m mypy src
	@echo "✅ Type checking complete!"

# Security checks
security-check:
	@echo "🔍 Checking dependencies for known vulnerabilities..."
	.venv/bin/python -m pip_audit
	@echo ""
	@echo "🔍 Scanning source code for security issues..."
	.venv/bin/python -m bandit -r src
	@echo ""
	@echo "✅ Security checks complete!"
