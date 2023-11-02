SHELL := /bin/bash

VERSION := 0.0.1
BUILD_INFO := Manual build

ENV_FILE := .env
ifeq ($(filter $(MAKECMDGOALS),config clean),)
	ifneq ($(strip $(wildcard $(ENV_FILE))),)
		ifneq ($(MAKECMDGOALS),config)
			include $(ENV_FILE)
			export
		endif
	endif
endif

clean: ## 🤖 Clean all caches and update packages
	@figlet $@ || true
	@py3clean . && rm -rf dist && poetry update

install: ## 🤖 Install dependencies
	@figlet $@ || true
	@rm -f poetry.lock && poetry install

build: ## 🤖 Build the project
	@figlet $@ || true
	@poetry build --format wheel
	@project_name=copilot-$$(poetry version -s)-py3-none-any.whl; \
		whl_file=$$(ls dist/$$project_name); \
		new_name="dist/copilot.whl"; \
		mv "$$whl_file" "$$new_name"; \
		echo "Renamed $$whl_file to $$new_name"

deploy: ## 🤖 Deploy the project locally
	@figlet $@ || true
	@make build && pip install dist/*.whl --force-reinstall

deploy-infra: ## 🤖 Deploy the required Azure infrastructure
	@figlet $@ || true
	@infrastructure/deploy.sh

extract-docs: ## 🤖 Extract the Azure CLI Documentation
	@figlet $@ || true
	@rm extract/docs -fdr && rm extract/yml -fdr && python3 extract/main.py