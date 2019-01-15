import argparse

from sqlflow.client import Client

parser = argparse.ArgumentParser()
parser.add_argument("--sql", type=str, help="sql", action="store", required=True)
parser.add_argument("--url", type=str, help="server url", action="store", required=True)


def main():
    args = parser.parse_args()

    client = Client(server_url=args.url)
    for res in client.execute(args.sql):
        print(res)


if __name__ == '__main__':
    main()
