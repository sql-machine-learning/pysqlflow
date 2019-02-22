SQLFLOW_VERSION := develop
VERSION_FILE := sqlflow/_version.py
SHELL := /bin/bash

setup: ## Setup virtual environment for local development
	python3 -m venv venv
	source venv/bin/activate \
	&& $(MAKE) install-requirements protoc

install-requirements:
	pip install -U -e .

test: ## Run tests
	python3 setup.py test

clean: ## Clean up temporary folders
	rm -rf build dist .eggs *.egg-info .pytest_cache sqlflow/proto

protoc: ## Generate python client from proto file
	python3 -m venv build/grpc
	source build/grpc/bin/activate \
	&& pip install grpcio-tools \
	&& python -m grpc_tools.protoc -Iproto --python_out=sqlflow/proto \
		--grpc_python_out=sqlflow/proto proto/sqlflow.proto\

release: ## Release new version
	$(if $(shell git status -s), $(error "Please commit your changes or stash them before you release."))

	# Remove dev from version number
	git checkout develop
	$(eval VERSION := $(subst .dev,,$(shell python -c "exec(open('$(VERSION_FILE)').read());print(__version__)")))
	$(info release $(VERSION)...)
	sed -i '' "s/, 'dev'//" $(VERSION_FILE)
	git commit -a -m "release $(VERSION)"

	# Merge to master
	git checkout master
	git merge develop
	git push origin master

	# Tag it
	git tag v$(VERSION)
	git push --tags

	# Bump version for development
	git checkout develop
	$(eval NEXT_VERSION := $(shell echo $(VERSION) | awk -F. '{print $$1"."($$2+1)".0"}'))
	$(eval VERSION_CODE := $(shell echo $(NEXT_VERSION) | sed 's/\./, /g'))
	sed -i '' -E "s/[0-9]+, [0-9]+, [0-9]+/$(VERSION_CODE), 'dev'/" $(VERSION_FILE)
	git commit -a -m "start $(NEXT_VERSION)"
	git push origin develop

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: help
.DEFAULT_GOAL := help
