import os

class LogWriter:
    @staticmethod
    def write_log(log_dir, table_name, delete_statement, identifier, verbose, cursor1, database, columns):
        log_filepath = os.path.join(log_dir, f"{table_name}_log.txt")
        with open(log_filepath, 'a', encoding='utf-8') as log_file:  # Open the file in write mode
            # Construct the DELETE statement
            delete_statement_with_values = delete_statement % identifier

            if verbose:
                print(f"Processing Identifier: {identifier}")
                print(f"DELETE STATEMENT: {delete_statement_with_values}")
                # Print information about the identified common row
                print(f"Common Row Information:")
                cursor1.execute(f"SELECT * FROM {database}.{table_name} WHERE {' AND '.join([f'{column} = %s' for column in columns])}", identifier)
                common_row = cursor1.fetchone()
                print(common_row)

            # Log the delete command to the file
            log_file.write(f"{delete_statement_with_values}\n")