import re

class DatabaseUtils:
    @staticmethod
    def get_database_names(cursor):
        """
        Retrieves the names of all databases in the server.

        Args:
            cursor: The database cursor.

        Returns:
            A list of database names.
        """
        cursor.execute("SHOW DATABASES")
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def get_table_names(cursor, database):
        """
        Retrieves the names of all tables in a specific database.

        Args:
            cursor: The database cursor.
            database: The name of the database.

        Returns:
            A list of table names.
        """
        cursor.execute(f"USE {database}")
        cursor.execute("SHOW TABLES")
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def exclude_databases(databases, exclude):
        """
        Excludes specific databases from a list of databases.

        Args:
            databases: The list of databases.
            exclude: The list of databases to exclude.

        Returns:
            A list of databases excluding the ones specified in the exclude list.
        """
        return [db for db in databases if db not in exclude]

    @staticmethod
    def parse_connection_string(connection_string):
        """
        Parses a connection string and extracts the user, password, host, and port.

        Args:
            connection_string: The connection string.

        Returns:
            A tuple containing the user, password, host, and port.

        Raises:
            ValueError: If the connection string is in an invalid format.
        """
        match = re.match(r'([^:@]+)(?::([^@]+))?@([^:]+):(\d+)', connection_string)
        if match:
            user, password, host, port = match.groups()
            return user, password, host, int(port)
        else:
            raise ValueError("Invalid connection string format")

    @staticmethod
    def table_exists(cursor, table_name, database):
        """
        Checks if a table exists in a specific database.

        Args:
            cursor: The database cursor.
            table_name: The name of the table.
            database: The name of the database.

        Returns:
            True if the table exists, False otherwise.
        """
        cursor.execute("SHOW TABLES IN {}".format(database))
        tables = [row[0] for row in cursor.fetchall()]
        return table_name in tables
