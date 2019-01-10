# SQLFlow Client Design Doc

## Overview

SQLFlow Client implements a minimum client that issues queries to and fetch results/logs from [sqlflowserver](https://github.com/wangkuiyi/sqlflowserver).

In `pysqlflow`, the client will be wrapped in the magic command where user directly writes SQL statements.

## Example

```python
import sqlflow

client = sqlflow.Client(server_url='localhost:50051')

# Regular SQL
response = client.execute('select * from table')
for dataframe in response:
    print(dataframe) # {'y': [4, 5, 6], 'x': [1, 2, 3]}

# ML SQL, prints epoch = ..., loss = ...
client.execute('select ... train ...')
```

## Implementation

`sqlflow.Client` uses grpc to contact the `sqlflowserver`. The service protocol is defined at [sqlflow.proto](https://github.com/wangkuiyi/sqlflowserver/blob/develop/sqlflow.proto).

`sqlflow.Client.__init__` establishes a grpc stub/channel based on `server_url`.

`sqlflow.Client.execute` takes a sql statement
- if the statement is a regular SQL, it returns a generator which generates dataframes
- if the statement is a extended SQL, it prints the log

`sqlflow.Client` can be implemented as
```python
class Client(object):
    def __init__(self, host):
        channel = grpc.insecure_channel(host)
        self._stub = sqlflow_pb2_grpc.SQLFlowStub(channel)

    def _decode_protobuf(self, proto):
        ...

    def execute(self, operation):
        for res in self._stub.Run(sqlflow_pb2.RunRequest(sql=operation)):
            if res.is_message():
                log(res)
            else:
                yield self._decode_protobuf(res)
```

