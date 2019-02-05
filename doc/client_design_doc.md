# SQLFlow Client Design Doc

## Overview

SQLFlow Client connects [sqlflowserver](https://github.com/wangkuiyi/sqlflowserver). It has two methods

1. `client.query` issues queries to and fetches rowset
   1. `SELECT * FROM …`
2. `client.execute` executes commands and prints logs
   1. `INSERT`,`DELETE`,`VIEW` and `DROP`
   2. `SELECT … TRAIN …` and `SELECT … PREDICT …`

## Example

```python
import sqlflow

client = sqlflow.Client(server_url='localhost:50051')

# Query SQL
rowset = client.query('SELECT ... FROM ...')
for row in rowset:
    print(row) # {[4, 5, 6]}

# Execution SQL, prints
# Query OK, ... row affected (... sec)
client.execute('DELETE FROM ... WHERE ...')

# ML SQL, prints
# epoch = 0, loss = ...
# epoch = 1, loss = ...
# ...
client.execute('SELECT ... TRAIN ...')
```

## Service Protocol

`sqlflow.Client` uses grpc to contact the `sqlflowserver`. The service protocol is defined as follows

```proto
syntax = "proto3";

import "google/protobuf/any.proto";

package server;

service SQLFlow {
  rpc Query (Request) returns (stream RowSet);
  rpc Execute (Request) returns (stream Messages);
}

// SQL statements to run
// e.g.
//      1. `SELECT ...`
//      2. `USE ...`, `DELETE ...`
//      3. `SELECT ... TRAIN/PREDICT ...`
message Request {
  string sql = 1;		// The SQL statement to be executed.
}

// SQL statements like `SELECT ...`, `DESCRIBE ...` returns a rowset.
// The rowset might be big. In such cases, Query returns a stream
// of RunResponse
message RowSet {
  repeated string column_names = 1;
  repeated Row rows = 2;

  // A row of data. Data can be any type
  message Row {
      repeated google.protobuf.Any data = 1;
  }
}

// SQL statements like `USE database`, `DELETE` returns only a success
// message.
//
// SQL statement like `SELECT ... TRAIN/PREDICT ...` returns a stream of
// messages which indicates the training/predicting progress
message Messages {
  repeated string messages = 1;
}
```

## Implementaion

`sqlflow.Client.__init__` establishes a grpc stub/channel based on `server_url`.

`sqlflow.Client.query` takes a sql statement and returns a `RowSet` object.

`sqlflow.Client.execute` takes a sql statement prints the reponses.
```python
class Client:
    def __init__(self, host):
        channel = grpc.insecure_channel(host)
        self._stub = sqlflow_pb2_grpc.SQLFlowStub(channel)

    def _decode_protobuf(self, proto):
        # decode rowset

    def query(self, operation):
        def rowset_gen():
            for res in self._stub.Query(sqlflow_pb2.Request(sql=operation)):
                yield self._decode_protobuf(res)
        return RowSet(rowset_gen=rowset_gen)

    def execute(self, operation):
        for res in self._stub.Query(sqlflow_pb2.Request(sql=operation)):
            log(res)

class RowSet:
    def __init__(self, rowset_gen):
        self._rowset_gen = rowset_gen

    def __repr__(self):
        # used for IPython: pretty prints self
```

## Credential

The authorization between the client and the server should be independent
with authorization between the server and the database. A client should never
store any sensitive data such as DB username and password.
