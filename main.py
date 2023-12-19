import sys
import mysql.connector
from sql_info import SQLInfo
from arg_parser import get_args
from database_utils import DatabaseUtils
from wordpress_analyze import WordpressAnalyze
from database_comparator import DatabaseComparator

# TODO: Add more wordpress-specific analysis MEDIUM-BIG
# TODO: Logging for SQLInfo and wordpress_analyze?? MEDIUM
# TODO: Add more comments to make code more readable SMALL
# TODO: Add more error handling MEDIUM
# TODO: Figure out verbose output situation SMALL
# TODO: Function to parse data? BIG
# TODO: Redo README SMALL
# TODO: Remove unecessary print statements/commented out code SMALL
# TODO: Create a database analysis type function. MEDIUM-BIG


def get_connection_details(server, args):
    user, password, host, port = DatabaseUtils.parse_connection_string(server)
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=args['database']
    )
    cursor = conn.cursor()
    return conn, cursor

def main():
    args, main_parser = get_args()

    conn1, cursor1 = get_connection_details(args['server1'], args)

    if args['server2']:
        conn2, cursor2 = get_connection_details(args['server2'], args)
    else:
        conn2, cursor2 = None, None

    if args['command'] == 'main':
        if not args['database']:
            print("Error: --database is required.")
            main_parser.print_help()
            sys.exit(1)
        DatabaseComparator.compare_databases_with_args(cursor1, cursor2, args)
    elif args.get('command') == 'wordpress':
        WordpressAnalyze(cursor1, cursor2, args).main()
    elif args.get('command') == 'information':
        SQLInfo(cursor1, cursor2, args).main()
    else:
        DatabaseComparator.compare_databases_with_args(cursor1, cursor2, args)

    if conn2:
        conn2.commit()
        conn2.close()

    conn1.commit()
    conn1.close()

if __name__ == "__main__":
    main()