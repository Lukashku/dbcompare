# Importing necessary modules
from database_utils import DatabaseUtils
from common_data_remover import CommonDataRemover

# Defining a class for comparing databases
class DatabaseComparator:
    # Method for comparing databases
    @staticmethod
    def compare_databases(cursor1, cursor2, database, table=None, exact=False, verbose=False, exclude=None):
        # Get the list of database names from both cursors
        databases1 = DatabaseUtils.get_database_names(cursor1)
        databases2 = DatabaseUtils.get_database_names(cursor2)

        # Exclude specified databases from the comparison
        if exclude:
            databases1 = DatabaseUtils.exclude_databases(databases1, exclude)
            databases2 = DatabaseUtils.exclude_databases(databases2, exclude)

        # Iterate over each database in the first cursor
        for db1 in databases1:
            # Check if the database exists in the second cursor
            if db1 not in databases2:
                print(f"Warning: Database {db1} in server1 does not exist in server2.")
                continue

            # Set the current database for both cursors
            cursor1.execute(f"USE {db1}")
            cursor2.execute(f"USE {db1}")

            # Get the list of table names from both cursors for the current database
            tables1 = DatabaseUtils.get_table_names(cursor1, db1)
            tables2 = DatabaseUtils.get_table_names(cursor2, db1)

            # Iterate over each table in the first cursor
            for t1 in tables1:
                # Check if the table exists in the second cursor
                if t1 not in tables2:
                    print(f"Warning: Table {t1} in database {db1} in server1 does not exist in server2.")
                    continue

                # Check if a specific table is specified or if the current table matches the specified table
                if table is None or (table and table == t1):
                    # Remove common data between the two tables
                    CommonDataRemover.remove_common_data(cursor1, cursor2, t1, db1, exact, verbose)

    # Method for comparing databases with arguments
    @staticmethod
    def compare_databases_with_args(cursor1, cursor2, args):
        # Get the list of all tables or the specified tables from the arguments
        all_tables = [x.strip() for x in args['table'].split(',')] if args.get('table') else DatabaseUtils.get_table_names(cursor1, args['database'])
        
        # Get the list of excluded tables from the arguments
        exclude_tables = [x.strip() for x in args['exclude'].split(',')] if args.get('exclude') else []
        
        # Filter the tables based on the excluded tables
        tables = [x for x in all_tables if x not in exclude_tables]
        
        # Print the tables and exclude_tables for debugging purposes
        print(tables)
        print(exclude_tables)
        
        # Iterate over each table and remove common data
        for table in tables:
            CommonDataRemover.remove_common_data(
                cursor1,
                cursor2,
                table,
                args['database'],
                args['verbose'],
                args['exclude'],
                args['log_output'],  # Pass the current working directory as the log_dir argument
                args['log'] 
        )
        
        # Print a message indicating the completion of the comparison
        print("Comparison complete.")