from arg_parser import get_args
import sys
import mysql.connector
from database_utils import DatabaseUtils
from common_data_remover import CommonDataRemover
from wordpress_analyze import WordpressAnalyze
from sql_info import SQLInfo
from database_comparator import DatabaseComparator

# TODO: Add more wordpress-specific analysis
# TODO: Add Table listing functionality  --- DONE
# TODO: Move Log file create to its own file
# TODO: Logging for SQLInfo and wordpress_analyze??
# TODO: Move compare_database to database_comparator.py??
# TODO: Add arguments to its own file
# TODO: Add more comments to make code more readable
# TODO: Add more error handling



# def compare_databases(cursor1, cursor2, args):
#     all_tables = [x.strip() for x in args['table'].split(',')] if args.get('table') else DatabaseUtils.get_table_names(cursor1, args['database'])
#     exclude_tables = [x.strip() for x in args['exclude'].split(',')] if args.get('exclude') else []
#     tables = [x for x in all_tables if x not in exclude_tables]
#     print(tables)

#     print(exclude_tables)
#     for table in tables:
            
#             #print(f"Table: {table}")
#             #print(f"Database {args['database']}")
#             CommonDataRemover.remove_common_data(
#                 cursor1,
#                 cursor2,
#                 table,
#                 args['database'],
#                 args['verbose'],
#                 args['exclude'],
#                 args['log_output']  # Pass the current working directory as the log_dir argument
#         )
#     print("Comparison complete.")

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