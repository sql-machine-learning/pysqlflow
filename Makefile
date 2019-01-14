SQLFLOW_VERSION := develop
SHELL := /bin/bash

setup:
	python3 -m venv venv
	source venv/bin/activate \
	&& $(MAKE) install-requirements protoc

install-requirements:
	pip install -U -e .

test:
	python3 setup.py test

clean:
	rm -rf build dist .eggs *.egg-info .pytest_cache sqlflow/proto

protoc:
	python3 -m venv build/grpc
	source build/grpc/bin/activate \
	&& pip install grpcio-tools \
	&& mkdir -p build/grpc/sqlflow/proto \
	&& curl -o build/grpc/sqlflow/proto/sqlflow.proto \
		https://raw.githubusercontent.com/wangkuiyi/sqlflowserver/$(SQLFLOW_VERSION)/sqlflow.proto \
	&& python -m grpc_tools.protoc -Ibuild/grpc --python_out=. \
		--grpc_python_out=. build/grpc/sqlflow/proto/sqlflow.proto \
	&& rm -rf build/grpc

release:
	$(if $(shell git status -s), $(error "Please commit your changes or stash them before you release."))
	git checkout develop
	$(eval VERSION := $(subst .dev,,$(shell python sqlflow/__version__.py)))
	$(info release $(VERSION)...)
	sed -i '' "s/, 'dev'//" sqlflow/__version__.py
	git commit -a -m "release $(VERSION)"
	git checkout master
	git merge develop
	git push origin develop master

.DEFAULT_GOAL := setup
