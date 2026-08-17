# ============================================================
# Fly-in - Makefile
# 42 Project - Drone Routing Simulation
# ============================================================

PYTHON      := python3
PIP         := $(PYTHON) -m pip
MAIN        := main.py
VENV_DIR    := venv
REQ_FILE    := requirements.txt

# ------------------------------------------------------------
# install: install project dependencies
# ------------------------------------------------------------
.PHONY: install
install:
	@if [ -f $(REQ_FILE) ]; then \
		$(PIP) install --upgrade pip; \
		$(PIP) install -r $(REQ_FILE); \
	else \
		echo "No $(REQ_FILE) found, skipping dependency install."; \
	fi

# ------------------------------------------------------------
# run: execute the main script
# ------------------------------------------------------------
.PHONY: run
run:
	$(PYTHON) $(MAIN)

# ------------------------------------------------------------
# debug: run the main script under pdb
# ------------------------------------------------------------
.PHONY: debug
debug:
	$(PYTHON) -m pdb $(MAIN)

# ------------------------------------------------------------
# lint: mandatory flake8 + mypy check
# ------------------------------------------------------------
.PHONY: lint
lint:
	flake8 .
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

# ------------------------------------------------------------
# lint-strict: optional, stricter mypy checking
# ------------------------------------------------------------
.PHONY: lint-strict
lint-strict:
	flake8 .
	mypy . --strict

# ------------------------------------------------------------
# clean: remove caches and temporary files
# ------------------------------------------------------------
.PHONY: clean
clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: all
all: install run
