# For Linting
.PHONY: lint
lint:
	@echo "Running flake8"
	@flake8 ./porunga_cli

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
	@export PYPI_TOKEN=${{ secrets.PYPI_TOKEN }} && poetry publish --no-interaction --username __token__ --password $$PYPI_TOKEN
# Define a help target to show usage
.PHONY: help
help:
	@echo "Makefile targets:"
	@echo "  lint     - Run Python linter"
	@echo "  clean    - Clean up build artifacts"
	@echo "  help     - Show this help message"
	@echo "	 build	  - Build package"
	@echo "  publish  - Publish package"