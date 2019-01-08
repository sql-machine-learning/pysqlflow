from dbapi import Connection

def main():
    connection = Connection(host='localhost:50051')
    cursor = connection.cursor()
    cursor.execute('select * from table')
    print(cursor._response)

if __name__ == '__main__':
    main()
