import logging


class CommonDataRemover:

    def remove_common_data(self, cursor1, cursor2, args, logger=None):
        """
        Removes common data between two database tables.

        Args:
            cursor1: The cursor for the first database connection.
            cursor2: The cursor for the second database connection.
            args: An object containing parsed command-line arguments.
            logger: An optional logging object.
        """

        if not isinstance(args, Namespace):
            raise TypeError("Arguments must be provided through a Namespace object")

        table1, table2 = self._get_table_names(args.database, args.table)

        if args.verbose:
            logger.info(f"Removing common data from tables:")
            logger.info(f"- {table1}")
            logger.info(f"- {table2}")

        self._remove_common_data_from_tables(cursor1, cursor2, table1, table2, args, logger)

    def _get_table_names(self, database, table):
        """
        Extracts table names from provided arguments.

        Args:
            database: The database name.
            table: The optional table name.

        Returns:
            A tuple containing the names of the first and second tables.
        """

        if table:
            return (f"{database}.{table}", f"{database}.{table}")
        else:
            tables = database.split(",")
            return (tables[0], tables[1])

    def _remove_common_data_from_tables(self, cursor1, cursor2, table1, table2, args, logger):
        """
        Performs the actual data removal operation on two specified tables.

        Args:
            cursor1: The cursor for the first database connection.
            cursor2: The cursor for the second database connection.
            table1: The name of the first table.
            table2: The name of the second table.
            args: An object containing parsed command-line arguments.
            logger: An optional logging object.
        """

        # Get primary key information for both tables
        primary_key1 = self._get_primary_key(cursor1, table1)
        primary_key2 = self._get_primary_key(cursor2, table2)

        # Compare data and prepare deletion statements
        delete_statements = []
        for row in self._get_data_from_table(cursor1, table1, args.exclude):
            matching_row = self._find_matching_row(cursor2, table2, row, primary_key1, primary_key2, args.exact)
            if matching_row:
                # Construct DELETE statement based on matching row
                delete_statements.append(f"DELETE FROM {table2} WHERE {primary_key2} = {matching_row[primary_key2]}")

        # Execute DELETE statements in batches
        batch_size = 100
        for i in range(0, len(delete_statements), batch_size):
            cursor2.executemany("\n".join(delete_statements[i:i + batch_size]))
            conn2.commit()

        if logger:
            logger.info(f"Removed {len(delete_statements)} rows from {table2}")

