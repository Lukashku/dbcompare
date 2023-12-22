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
# TODO: Add option to compare databases with different names
# TODO: Option to query data by date
# TODO: Allow wordpress to analyze a single database?
# TODO: Move priv check from analyze_db to db_utils
# TODO: Sanitize sql queries ??

def get_connection_details(server, args):
    # Parse the connection string to get the user, password, host, and port
    user, password, host, port = DatabaseUtils.parse_connection_string(server)
    
    # Establish a connection to the database
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=args['database']
    )
    
    # Create a cursor object
    cursor = conn.cursor()
    
    # Return the connection and cursor
    return conn, cursor

def main():
    # Parse the command line arguments
    args, main_parser = get_args()

    # Get the connection details for the first server
    conn1, cursor1 = get_connection_details(args['server1'], args)

    # If a second server is specified, get its connection details
    if args['server2']:
        conn2, cursor2 = get_connection_details(args['server2'], args)
    else:
        conn2, cursor2 = None, None

    # Execute the appropriate command based on the 'command' argument
    if args['command'] == 'main':
        if not args['database']:
            print("Error: --database is required.")
            main_parser.print_help()
            sys.exit(1)
        print("\n" + "-" * 80)
        print("WARNING: This option will potentially delete data from the --server1 database.")
        print("-" * 80)
        if input("Are you sure you want to continue? (y/n)").lower() == 'y':
            DatabaseComparator.compare_databases_with_args(cursor1, cursor2, args)
        else:
            return
    elif args.get('command') == 'wordpress':
        WordpressAnalyze(cursor1, args, cursor2).main()
    elif args.get('command') == 'information':
        SQLInfo(cursor1, cursor2, args).main()
    else:
        DatabaseComparator.compare_databases_with_args(cursor1, cursor2, args)

    # If a second connection was established, commit any changes and close it
    if conn2:
        conn2.commit()
        conn2.close()

    # Commit any changes and close the first connection
    conn1.commit()
    conn1.close()

# If this script is run directly (not imported as a module), call the main function
if __name__ == "__main__":
    main()