# ==============================
# Project Configuration Section
# ==============================
PROJECT_NAME := rongcloud-server-mcp-python
MODULE_NAME := rongcloud_server_mcp
VENV_DIR := .venv
PYTHON := python3
UV := uv
MCP := mcp

# ==============================
# Environment Management
# ==============================
.PHONY: venv
venv:
	@echo "Creating virtual environment using uv..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(UV) venv $(VENV_DIR); \
	else \
		echo "Virtual environment already exists at $(VENV_DIR)"; \
	fi
	@echo "\nActivate with:\nsource $(VENV_DIR)/bin/activate  # Linux/macOS\n.\\$(VENV_DIR)\\Scripts\\activate  # Windows"

# Sync all dependencies (including dev and extras)
.PHONY: sync
sync: venv
ifeq ($(MODE),prod)
	@echo "Syncing PRODUCTION dependencies..."
	@$(UV) sync
else
	@echo "Syncing DEVELOPMENT dependencies..."
	@$(UV) sync  --dev
endif

# Install project in editable mode with development dependencies (default)
# or production mode if MODE=prod is set
.PHONY: install
install: venv
ifeq ($(MODE),prod)
	@echo "Installing project in production mode..."
	@$(UV) pip install .
else
	@echo "Installing project in development mode..."
	@$(UV) pip install -e ".[dev]"
endif

# ==============================
# Development Workflow
# ==============================
.PHONY: dev
dev:
	@. $(VENV_DIR)/bin/activate && $(MCP) dev src/$(MODULE_NAME)/server.py

.PHONY: format
format:
	@. $(VENV_DIR)/bin/activate && \
	ruff format src/ tests/ && \
	ruff format src/ tests/

# ==============================
# Testing & Quality Assurance
# ==============================
.PHONY: test
test:
	@. $(VENV_DIR)/bin/activate && pytest -v tests/

.PHONY: lint
lint:
	@. $(VENV_DIR)/bin/activate && ruff check src/ tests/

.PHONY: fix
fix:
	@. $(VENV_DIR)/bin/activate && ruff check src/ tests/ --fix

# ==============================
# Build & Release
# ==============================
.PHONY: build
build:
	@. $(VENV_DIR)/bin/activate && $(UV) pip install --upgrade build
	@$(UV) run scripts/update_version.py
	@$(UV) run python -m build

.PHONY: publish
publish: build
	@. $(VENV_DIR)/bin/activate && $(UV) pip install --upgrade twine
	@twine upload dist/*

# ==============================
# Cleanup
# ==============================
.PHONY: clean
clean:
	@rm -rf build/ dist/ *.egg-info/
	@rm -rf $(VENV_DIR)
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.pyc' -delete

.PHONY: uninstall
uninstall:
	@. $(VENV_DIR)/bin/activate && $(UV) pip uninstall $(PROJECT_NAME)

