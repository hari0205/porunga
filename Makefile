# For Linting
.PHONY: lint
lint:
	@echo "Running flake8"
	@flake8 ./porunga

# Clean pyc and pycache
.PHONY: clean
clean:
	@echo "Clean pyc"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +

# For building
.PHONY: build
build:
	@echo "Building package"
	@poetry build

# For publishing
.PHONY: publish
publish:
	@echo "Publishing package"
	@poetry publish
# Define a help target to show usage
.PHONY: help
help:
	@echo "Makefile targets:"
	@echo "  lint     - Run Python linter"
	@echo "  clean    - Clean up build artifacts"
	@echo "  help     - Show this help message"