from connection import Connection

import sqlflow_pb2
import sqlflow_pb2_grpc

import grpc


def main():
    connection = Connection(host='localhost:50051')
    cursor = connection.cursor()
    cursor.execute('select * from table')
    print(cursor._response)

if __name__ == '__main__':
    main()
