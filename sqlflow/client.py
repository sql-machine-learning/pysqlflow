import argparse
import sys
import logging

import grpc
import sqlflow_pb2
import sqlflow_pb2_grpc
import google.protobuf.wrappers_pb2 as wrapper

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, help="server url", action="store", required=True)

#TODO(tonyyang-svail): move logging config elsewhere
logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    stream=sys.stdout,
    level=logging.DEBUG)


class Client(object):
    def __init__(self, server_url):
        channel = grpc.insecure_channel(server_url)
        self._stub = sqlflow_pb2_grpc.SQLFlowStub(channel)

    def _decode_any(self, a):
        if a.Is(wrapper.Int64Value.DESCRIPTOR):
            m = wrapper.Int64Value()
            a.Unpack(m)
            return m.value
        else:
            #TODO(tonyyang-svail): support more data types
            raise NotImplementedError

    def _decode_protobuf(self, res):
        dataframe = {}
        for key, value in res.columns.columns.iteritems():
            dataframe[key] = [self._decode_any(a) for a in value.data]
        return dataframe

    def execute(self, operation):
        for res in self._stub.Run(sqlflow_pb2.RunRequest(sql=operation)):
            if res.WhichOneof('response') == 'messages':
                for m in res.messages.messages:
                    logging.info(m)
            else:
                yield self._decode_protobuf(res)


def main():
    args = parser.parse_args()

    client = Client(server_url=args.url)

    logging.info('Standard SQL, prints dataframes')
    response = client.execute('select * from t')
    for dataframe in response:
        logging.info(dataframe) # {'y': [4, 5, 6], 'x': [1, 2, 3]}

    logging.info('Extended SQL, prints epoch = ..., loss = ...')
    # TODO(tonyyang-svail): avoid for loop
    for log in client.execute('SELECT * TRAIN .'):
        pass


if __name__ == '__main__':
    main()
