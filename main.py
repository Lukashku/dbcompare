import argparse
import sys
import mysql.connector
from database_utils import DatabaseUtils
from common_data_remover import CommonDataRemover
from wordpress_analyze import WordpressAnalyze
from sql_info import SQLInfo

# TODO: Add more wordpress-specific analysis
# TODO: Add Table listing functionality
# TODO: Add OpenAPI Key checking
# TODO: Move Log file create to its own file
# TODO: Logging for SQLInfo and wordpress_analyze??
# TODO: Move compare_database to database_comparator.py??
# TODO: Add arguments to its own file
# TODO: Add more comments to make code more readable
# TODO: Add more error handling



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

    main_parser = argparse.ArgumentParser(description='Compare and remove common data between two MySQL databases.')
    subparsers = main_parser.add_subparsers(dest='command')
    # Create the parser for the "main" command
    main_parser_main = subparsers.add_parser('main', help='Main command')
    main_parser_main.add_argument('--server1', required=True, help='Connection string for server1, e.g., user:password@host:port')
    main_parser_main.add_argument('--server2', required=False, help='Connection string for server2, e.g., user:password@host:port')
    main_parser_main.add_argument('--verbose', action='store_true', help='Enable verbose output')
    main_parser_main.add_argument('--status-key', default='s', help='Key to trigger status update (default is "s")')
    main_parser_main.add_argument('--database', required=True, help='Databases to compare, each specified separately')
    main_parser_main.add_argument('--table', help='Optional: Specify a specific table to compare')
    main_parser_main.add_argument('--exact', action='store_true', help='Enable exact matching, including the id column')
    main_parser_main.add_argument('--exclude', '-xt', dest='exclude', help='Tables to exclude, separated by commas')
    main_parser_main.add_argument('--log-output', default=None, help='The directory to output log files to')

    wordpress_parser = subparsers.add_parser('wordpress', help='Enable WordPress-specific analysis')
    wordpress_parser.add_argument('--basic', action='store_true', help='Perform basic WordPress analysis')
    wordpress_parser.add_argument('--wp-users', action='store_true', help='Analyzes the wp_users table')
    wordpress_parser.add_argument('--wp-options', action='store_true', help='Analyzes the wp_options table')

    # Subparser for the 'information' command
    info_parser = subparsers.add_parser('information', help='Fetch information about and/or query the database(s)')
    info_parser.add_argument('--server1', help='The first server')
    info_parser.add_argument('--server2', required=False, help='The second server (optional)')
    info_parser.add_argument('-db', '--database', help='The database')
    info_parser.add_argument('--sql-query', nargs='?', default=None, help='The query to execute (optional, only if --openai is passed)')
    info_parser.add_argument('--openai', action='store_true', help='Use OpenAI to generate the SQL query (Experimental)')
    info_parser.add_argument('-L', '--list', action='store_true', help='List databases from the specified server(s)')
    info_parser.add_argument('-T', '--tables', action='store_true', help='List tables from the specified database')

    args = vars(main_parser.parse_args())

    user1, password1, host1, port1 = DatabaseUtils.parse_connection_string(args['server1'])

    conn1 = mysql.connector.connect(
        host=host1,
        user=user1,
        password=password1,
        port=port1,
        database=args['database']
    )

    if args['server2']:
        user2, password2, host2, port2 = DatabaseUtils.parse_connection_string(args['server2'])
        conn2 = mysql.connector.connect(
            host=host2,
            user=user2,
            password=password2,
            port=port2,
            database=args['database']
        )
        cursor2 = conn2.cursor()
    else:
        user2, password2, host2, port2 = None, None, None, None
        conn2 = None
        cursor2 = None

    cursor1 = conn1.cursor()

    if args['command'] == 'main':

        if not args['database']:
            print("Error: --database is required.")
            main_parser.print_help()
            sys.exit(1)

    elif args.get('command') == 'wordpress':
        wordpress_analyzer = WordpressAnalyze(cursor1, cursor2, args)
        if args['wp_users']:
            wordpress_analyzer.wp_users()
        if args['wp_options']:
            wordpress_analyzer.wp_options()
        else:
            print("Error: No command specified.")
            wordpress_parser.print_help()
            sys.exit(1)

    elif args.get('command') == 'information':
        SQLInfo(cursor1, cursor2, args).main()
    else:
        compare_databases(cursor1, cursor2, args)

    if conn2:
        conn2.commit()
        conn2.close()

    conn1.commit()
    conn1.close()

if __name__ == "__main__":
    main()