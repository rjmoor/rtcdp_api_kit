# Makefile for project utilities

# Variables
PYTHON = python
CLEANUP_SCRIPT = ../cleanup_manager.py  # relative path to cleanup_manager.py
ROOT_DIR = ../rtcdp  # where your real source lives

.PHONY: help clean lint slice move full-clean

help:
	@echo "🛠️  Available commands:"
	@echo "  make clean         - Remove __pycache__ folders"
	@echo "  make init          - Ensure __init__.py exists"
	@echo "  make lint          - Auto-format code with black"
	@echo "  make slice FILE=path/to/file MAX=1000 - Slice a big file"
	@echo "  make move OLD=old_path NEW=new_path - Move or rename files"
	@echo "  make full-clean    - Run full project cleanup"

clean:
	$(PYTHON) $(CLEANUP_SCRIPT) --remove-pycache --root $(ROOT_DIR)

init:
	$(PYTHON) $(CLEANUP_SCRIPT) --ensure-init --root $(ROOT_DIR)

lint:
	$(PYTHON) $(CLEANUP_SCRIPT) --lint --root $(ROOT_DIR)

full-clean:
	$(PYTHON) $(CLEANUP_SCRIPT) --full-clean --root $(ROOT_DIR)

slice:
	$(PYTHON) $(CLEANUP_SCRIPT) --slice $(FILE) $(MAX)

move:
	$(PYTHON) $(CLEANUP_SCRIPT) --move $(OLD) $(NEW)
