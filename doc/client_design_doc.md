# SQLFlow Client Design Doc

## Overview

SQLFlow Client implements a minimum client that issues queries to and fetch results/logs from [sqlflowserver](https://github.com/wangkuiyi/sqlflowserver).

In `pysqlflow`, the client will be wrapped in the magic command where user directly writes SQL statements.

## Example

```python
import sqlflow

client = sqlflow.Client(address='localhost:50051')

# Regular SQL
response = client.query('select * from table')
for dataframe in response:
    print(dataframe) # {'y': [4, 5, 6], 'x': [1, 2, 3]}

# ML SQL
response = client.query('select ... train ...')
for log in response:
    print(log) # epoch = ..., loss = ...
```

## Implementation

`sqlflow.Client` uses grpc to contact the `sqlflowserver`. The service protocol is defined at [sqlflow.proto](https://github.com/wangkuiyi/sqlflowserver/blob/develop/sqlflow.proto).

`sqlflow.Client.__init__` establishes a grpc stub/channel based on service's ip address and port number.

`sqlflow.Client.query` takes a sql string and returns a `sqlflow.Response` instance. `sqlflow.Response.__iter__` is overloaded to provide iteration.

`sqlflow.Client` and `sqlflow.Response` can be implemented as
```python
class Client(object):
    def __init__(self, host):
        channel = grpc.insecure_channel(host)
        self._stub = sqlflow_pb2_grpc.SQLFlowStub(channel)

    def query(self, query):
        return Response(self._stub.Run(sqlflow_pb2.RunRequest(sql=operation)))

class Response(object):
    def __init__(self, response):
        self._response = response
    
    def _decode_protobuf(self, proto):
        ...

    def __iter__(self):
        for res_proto in self.response:
            return self._decode_protobuf(res_proto)
```

