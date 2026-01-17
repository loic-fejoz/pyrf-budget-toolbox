.PHONY: help install lint format test quarto clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the project in editable mode
	uv pip install -e .

lint: ## Run ruff check
	uv run ruff check .

format: ## Run ruff format
	uv run ruff format .

test: ## Run pytest
	uv run pytest

quarto: ## Render all Quarto examples
	uv run quarto render examples/*.qmd

quarto-preview-feasibility_5km_link: ## Preview a Quarto example
	uv run quarto preview examples/feasibility_5km_link.qmd --no-browser

clean: ## Remove temporary files and build artifacts
	rm -rf .ruff_cache
	rm -rf .pytest_cache
	rm -rf .venv
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.svg" -delete
	find . -type f -name "*.png" -delete
	find . -type f -name "*.html" -delete
