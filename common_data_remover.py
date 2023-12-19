import os
import mysql.connector
from log_writer import LogWriter


class CommonDataRemover:
    total_deleted_lines = 0

    @staticmethod
    def table_exists(cursor, table_name, database):
        cursor.execute("SHOW TABLES IN {}".format(database))
        tables = [item[0] for item in cursor.fetchall()]
        return table_name in tables
    
    @staticmethod
    def remove_common_data(cursor1, cursor2, table_name, database, verbose, exclude, log_filepath=None, log_enabled=False):

        # Fetch column names from information_schema
        try:
            cursor1.execute(f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = '{database}'")
            columns = [column[0] for column in cursor1.fetchall()]
            print(columns)

            # Check if the first column is 'id' or 'ID' and exclude it from comparisons
            columns_to_exclude = ['id'] if columns and columns[0].lower() == 'id' and not exclude else []

            # Construct the DELETE statement
            delete_conditions = " AND ".join([f"{column} = %s" for column in columns if column.lower() not in columns_to_exclude])
            delete_statement = f"DELETE FROM {database}.{table_name} WHERE {delete_conditions}" if delete_conditions else f"DELETE FROM {database}.{table_name}"

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

            # In the file where you call write_log method
            if log_enabled:
                if log_filepath is None:
                    log_filepath = os.path.join(os.getcwd(), "logs", database)
                os.makedirs(log_filepath, exist_ok=True)  # Ensure the directory exists

                for identifier in common_identifiers:
                    cursor1.execute(delete_statement, identifier)
                    count += 1
                    CommonDataRemover.total_deleted_lines += 1  # Update the class attribute

                    LogWriter.write_log(log_filepath, table_name, delete_statement, identifier, verbose, cursor1, database, columns)

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

