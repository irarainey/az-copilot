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

build: ## 🤖 Build the project
	@figlet $@ || true
	@poetry build

clean: ## 🤖 Clean all caches and update packages
	@figlet $@ || true
	@py3clean . && rm -rf dist && poetry update

install: ## 🤖 Install dependencies
	@figlet $@ || true
	@rm -f poetry.lock && poetry install

all:
	@figlet $@ || true
	@make clean && make install && make build