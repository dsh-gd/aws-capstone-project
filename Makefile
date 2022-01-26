# Makefile
.PHONY: help
help:
	@echo "Commands:"
	@echo "venv   : creates development environment."
	@echo "layer  : creates Lambda layer."
	@echo "style  : runs style formatting."
	@echo "clean  : cleans all unecessary files."

# Environment
.ONESHELL:
venv:
	python3 -m venv venv
	source venv/bin/activate && \
	python -m pip install --upgrade pip setuptools wheel && \
	python -m pip install -e ".[dev]" --no-cache-dir

# Lambda layer
layer:
	chmod +x build_layer.sh
	./build_layer.sh

# Styling
.PHONY: style
style:
	black .
	flake8
	isort .

# Cleaning
.PHONY: clean
clean: style
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf
