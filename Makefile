SQLFLOW_VERSION := develop

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

.DEFAULT_GOAL := setup
