# ============================================================================ #
#                                   FLY-IN                                     #
# ============================================================================ #

# Package manager and environment runner via uv
UV              := uv
PYTHON          := $(UV) run python

# Default map fallback (supports both MAP=... and maps=... from CLI)
MAP             ?= maps/easy/02_simple_fork.txt
ifdef maps
override MAP    := $(maps)
endif

# Source files for linters
PY_FILES        := main.py \
                   fly_in/factories.py \
                   fly_in/parsing.py \
                   fly_in/pathfinding.py \
                   fly_in/simulation.py \
                   fly_in/visualiser.py

# Suppress Pygame greeting banner in terminal
export PYGAME_HIDE_SUPPORT_PROMPT := hide

# Subject-compliant mypy flags (Chapter III.2)
MYPY_FLAGS      := --warn-return-any \
                   --warn-unused-ignores \
                   --ignore-missing-imports \
                   --disallow-untyped-defs \
                   --check-untyped-defs

# Declare phony targets (prevent conflicts with files of the same name)
.PHONY: all install run debug visualize test lint lint-strict clean fclean re help

# ============================================================================ #
#                                MAIN TARGETS                                  #
# ============================================================================ #

# Default target: sets up the virtual environment
all: install

# III.2: install — Synchronize dependencies using uv
install:
	@echo "==> [install] Syncing dependencies and virtual environment with uv..."
	@$(UV) sync
	@echo "==> [install] Environment successfully installed."

# III.2: run — Run main simulation (usage: make run MAP=path/to/map.txt)
run:
	@echo "==> [run] Starting drone simulation engine on map: $(MAP)"
	@$(PYTHON) main.py $(MAP)

# III.2: debug — Run simulation under Python interactive debugger (pdb)
debug:
	@echo "==> [debug] Launching debugger (pdb) for map: $(MAP)"
	@$(PYTHON) -m pdb main.py $(MAP)

# Run Pygame graphic visualizer
visualize:
	@echo "==> [visualize] Launching graphical visualizer for map: $(MAP)"
	@$(PYTHON) fly_in/visualiser.py $(MAP)

# III.3: Run automated test suite with pytest
test:
	@echo "==> [test] Running test suite via pytest..."
	@$(UV) run pytest -v
	@echo "==> [test] All tests completed."

# ============================================================================ #
#                               CODE QUALITY                                   #
# ============================================================================ #

# III.2: lint — Mandatory subject style check (flake8) and static typing (mypy)
lint:
	@echo "==> [lint] Checking code style with flake8..."
	@$(UV) run flake8 $(PY_FILES)
	@echo "==> [lint] Checking static types with mypy (subject flags)..."
	@$(UV) run mypy $(PY_FILES) $(MYPY_FLAGS)
	@echo "==> [lint] Linting checks passed successfully."

# III.2: lint-strict — Strict type check (mypy --strict)
lint-strict:
	@echo "==> [lint-strict] Checking code style with flake8..."
	@$(UV) run flake8 $(PY_FILES)
	@echo "==> [lint-strict] Running strict static type analysis (mypy --strict)..."
	@$(UV) run mypy $(PY_FILES) --strict
	@echo "==> [lint-strict] Strict type checking passed with zero errors."

# ============================================================================ #
#                                 CLEANUP                                      #
# ============================================================================ #

# III.2: clean — Remove cache directories and bytecode files
clean:
	@echo "==> [clean] Removing bytecode, caches, and temporary files..."
	@rm -rf .pytest_cache .mypy_cache .ruff_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "==> [clean] Project workspace cleaned."

# fclean — Full cleanup including the virtual environment (.venv)
fclean: clean
	@echo "==> [fclean] Purging virtual environment (.venv)..."
	@rm -rf .venv
	@echo "==> [fclean] Full cleanup complete."

# re — Rebuild environment from scratch
re: fclean all

# ============================================================================ #
#                                 HELP MENU                                    #
# ============================================================================ #

help:
	@echo "Fly-In Build & Execution Automation"
	@echo "-----------------------------------"
	@echo "Available commands:"
	@echo "  make install             Install dependencies and setup venv via uv"
	@echo "  make run [MAP=path]      Run drone simulation on the target map"
	@echo "  make visualize [MAP=path] Launch GUI visualizer"
	@echo "  make debug [MAP=path]    Debug simulation with pdb"
	@echo "  make test                Execute pytest suite"
	@echo "  make lint                Run flake8 and mypy with subject flags"
	@echo "  make lint-strict         Run mypy with --strict flag"
	@echo "  make clean               Remove build and cache artifacts"
	@echo "  make fclean              Remove cache and purge .venv"
	@echo "  make re                  Purge and reinstall everything"
