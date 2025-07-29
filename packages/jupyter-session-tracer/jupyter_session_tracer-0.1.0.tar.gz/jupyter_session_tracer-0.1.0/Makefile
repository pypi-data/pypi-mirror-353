.PHONY: help install develop build clean lint test build-wheel

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	jlpm install

develop: ## Set up for development
	@./scripts/develop.sh

build: ## Build the extension
	@./scripts/build.sh

build-wheel: ## Build wheel package for distribution
	@./scripts/build-wheel.sh

clean: ## Clean build artifacts
	jlpm clean:all
	rm -rf build/ dist/ *.egg-info/

lint: ## Run linting
	jlpm lint

lint-fix: ## Run linting with auto-fix
	jlpm prettier && jlpm eslint

watch: ## Watch for changes during development
	jlpm watch

lab: ## Start JupyterLab
	jupyter lab

test-install: ## Test the built extension
	pip install dist/*.whl --force-reinstall
	jupyter labextension list 