import argparse

from sqlflow.client import Client

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, help="server url", action="store", required=True)

def main():
    args = parser.parse_args()

    client = Client(server_url=args.url)

    print('Standard SQL, prints dataframes')
    response = client.execute('select * from t')
    for dataframe in response:
        print(dataframe) # {'y': [4, 5, 6], 'x': [1, 2, 3]}

    print('Extended SQL, prints epoch = ..., loss = ...')
    # TODO(tonyyang-svail): avoid for loop
    for log in client.execute('SELECT * TRAIN .'):
        pass

if __name__ == '__main__':
    main()
