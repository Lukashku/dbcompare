import mysql.connector
import os

class CommonDataRemover:
    def __init__(self):
        self.total_deleted_lines = 0

    @staticmethod
    def table_exists(cursor, table_name, database):
        cursor.execute("SHOW TABLES IN {}".format(database))
        tables = [item[0] for item in cursor.fetchall()]
        return table_name in tables

    def remove_common_data(self, cursor1, cursor2, table_name, database, args, verbose=False, exclude=None, log_filepath=None):
        # Set default logfile path if not provided
        if log_filepath is None:
            log_filepath = os.path.join(os.getcwd(), 'logfile.txt')

        # Fetch column names from information_schema
        try:
            # Extract necessary values from args
            column_query = "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME = %s AND TABLE_SCHEMA = %s"
            cursor1.execute(column_query, (table_name, database))
            columns = [column[0] for column in cursor1.fetchall()]

            # Check if the first column is 'id' or 'ID' and exclude it from comparisons
            if columns and columns[0].lower() == 'id' and not args.exact:
                columns_to_exclude = ['id']
            else:
                columns_to_exclude = []

            # Construct the DELETE statement
            delete_conditions = " AND ".join([f"{column} = %s" for column in columns if column.lower() not in columns_to_exclude])

            if delete_conditions:
                delete_statement = f"DELETE FROM {database}.{table_name} WHERE {delete_conditions}"
            else:
                # No columns to exclude, delete all rows
                delete_statement = f"DELETE FROM {database}.{table_name}"

            # Convert boolean values to integers for SQL query
            args_exact_int = 1 if args.exact else 0

            # Fetch and remove common data
            cursor1.execute(f"SELECT * FROM {database}.{table_name}")
            data1 = set(tuple(cell if not isinstance(cell, bytearray) else bytes(cell) for cell in row) for row in cursor1.fetchall())

            cursor2.execute(f"SELECT * FROM {database}.{table_name}")
            data2 = set(tuple(cell if not isinstance(cell, bytearray) else bytes(cell) for cell in row) for row in cursor2.fetchall())

            # Create a set of identifiers for each row based on non-excluded columns
            identifier_func = lambda row: tuple(value for column, value in zip(columns, row) if column.lower() not in columns_to_exclude)
            unique_data1 = set(identifier_func(row) for row in data1)
            unique_data2 = set(identifier_func(row) for row in data2)

            # Find the common identifiers and execute the DELETE statement for each
            common_identifiers = unique_data1.intersection(unique_data2)

            count = 0

            print(f"Table: {table_name}")
            print(f"Common Identifiers: {common_identifiers}")

            if log_filepath:
                with open(log_filepath, "a") as log_file:
                    for identifier in common_identifiers:
                        print(f"Processing Identifier: {identifier}")
                        cursor1.execute(delete_statement, identifier)
                        count += 1
                        self.total_deleted_lines += 1  # Update the class attribute

                        if verbose:
                            # Construct and print the DELETE statement
                            delete_statement_with_values = delete_statement % identifier
                            print(f"DELETE STATEMENT: {delete_statement_with_values}")

                            # Print information about the identified common row
                            print(f"Common Row Information:")
                            cursor1.execute(f"SELECT * FROM {database}.{table_name} WHERE {' AND '.join([f'{column} = %s' for column in columns])}", identifier)
                            common_row = cursor1.fetchone()
                            print(common_row)

                            # Log the delete command to the file
                            log_file.write(f"{delete_statement_with_values}\n")

                # Print information about the process
                print(f"Processed {count} common rows in table {table_name}")

        except mysql.connector.errors.ProgrammingError as e:
            # Handle the table not found error
            if "Table" in str(e) and "doesn't exist" in str(e):
                print(f"Table {table_name} doesn't exist in {database}. Skipping...")
            else:
                # For other ProgrammingError exceptions, raise the error
                raise e

# Instantiate CommonDataRemover
common_data_remover = CommonDataRemover()

