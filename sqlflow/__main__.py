import argparse

from sqlflow.client import Client

parser = argparse.ArgumentParser()
parser.add_argument('sql', nargs='+', type=str, help="sql", action="store")
parser.add_argument("--url", type=str, help="server url", action="store", default=None)
parser.add_argument("--ca_crt", type=str, help="Path to CA certificates of SQLFlow client.", action="store", default=None)

def main():
    args = parser.parse_args()

    client = Client(server_url=args.url, ca_crt=args.ca_crt)
    for sql in args.sql:
        print("executing: {}".format(sql))
        for res in client.execute(sql):
            print(res)
