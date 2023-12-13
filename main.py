import argparse
import mysql.connector
from prettytable import PrettyTable
from database_utils import DatabaseUtils
from common_data_remover import CommonDataRemover
import sys
import os


def list_databases(server, user, password, host, port):
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port
    )
    cursor = conn.cursor()
    databases = DatabaseUtils.get_database_names(cursor)

    table = PrettyTable(["Databases on {}".format(server)])
    table.align["Databases on {}".format(server)] = 'r'
    for database in databases:
        table.add_row([database])

    conn.close()
    return table

def compare_databases(cursor1, cursor2, args):
    all_tables = [x.strip() for x in args['table'].split(',')] if args.get('table') else DatabaseUtils.get_table_names(cursor1, args['database'])
    exclude_tables = [x.strip() for x in args['exclude'].split(',')] if args.get('exclude') else []
    tables = [x for x in all_tables if x not in exclude_tables]
    print(tables)

    print(exclude_tables)
    for table in tables:
            
            #print(f"Table: {table}")
            #print(f"Database {args['database']}")
            CommonDataRemover.remove_common_data(
                cursor1,
                cursor2,
                table,
                args['database'],
                args['verbose'],
                args['exclude'],
                args['log_output']  # Pass the current working directory as the log_dir argument
        )
    print("Comparison complete.")

def main():
    parser = argparse.ArgumentParser(description='Compare and remove common data between two MySQL databases.')
    parser.add_argument('--server1', required=True, help='Connection string for server1, e.g., user:password@host:port')
    parser.add_argument('--server2', required=True, help='Connection string for server2, e.g., user:password@host:port')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--status-key', default='s', help='Key to trigger status update (default is "s")')
    parser.add_argument('--database', help='Databases to compare, each specified separately')
    parser.add_argument('--table', help='Optional: Specify a specific table to compare')
    parser.add_argument('--exact', action='store_true', help='Enable exact matching, including the id column')
    parser.add_argument('--exclude', '-xt', dest='exclude', help='Tables to exclude, separated by commas')
    parser.add_argument('-L', '--list', action='store_true', help='List databases from each server and exit')
    parser.add_argument('--log-output', default=None, help='The directory to output log files to')

    args = vars(parser.parse_args())

    if args['list']:
        user1, password1, host1, port1 = DatabaseUtils.parse_connection_string(args['server1'])
        user2, password2, host2, port2 = DatabaseUtils.parse_connection_string(args['server2'])

        table_server1 = list_databases("Server 1", user1, password1, host1, port1)
        table_server2 = list_databases("Server 2", user2, password2, host2, port2)

        max_rows = max(len(table_server1._rows), len(table_server2._rows))
        for i in range(max_rows):
            row1 = table_server1._rows[i] if i < len(table_server1._rows) else ['']
            row2 = table_server2._rows[i] if i < len(table_server2._rows) else ['']

            print(f"{row1[0]:<40}{row2[0]:>40}")

        return

    if not args['database']:
        print("Error: --database is required.")
        parser.print_help()
        sys.exit(1)

    user1, password1, host1, port1 = DatabaseUtils.parse_connection_string(args['server1'])
    user2, password2, host2, port2 = DatabaseUtils.parse_connection_string(args['server2'])

    conn1 = mysql.connector.connect(
        host=host1,
        user=user1,
        password=password1,
        port=port1,
        database=args['database']
    )

    conn2 = mysql.connector.connect(
        host=host2,
        user=user2,
        password=password2,
        port=port2,
        database=args['database']
    )

    cursor1 = conn1.cursor()
    cursor2 = conn2.cursor()

    compare_databases(cursor1, cursor2, args)

    conn1.commit()
    conn1.close()
    conn2.close()

if __name__ == "__main__":
    main()