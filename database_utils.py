import mysql.connector

class DatabaseUtils:

    @staticmethod
    def connect_and_list_databases(connection_string):
        """
        Connects to a database and lists available databases.

        Args:
            connection_string: The database connection string.

        Returns:
            A list of database names.
        """

        with mysql.connector.connect(**parse_connection_string(connection_string)) as conn:
            cursor = conn.cursor()
            cursor.execute("SHOW DATABASES")
            return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def parse_connection_string(connection_string):
        """
        Parses a connection string into individual components.

        Args:
            connection_string: The database connection string.

        Returns:
            A dictionary containing parsed connection parameters.
        """

        parts = connection_string.split(":", 4)
        return {
            "user": parts[0],
            "password": parts[1],
            "host": parts[2],
            "port": int(parts[3]),
            "database": parts[4] if len(parts) > 4 else None,
        }

    @staticmethod
    def connect_to_databases(server1_connection_string, server2_connection_string):
        """
        Connects to two databases based on provided connection strings.

        Args:
            server1_connection_string: The connection string for server 1.
            server2_connection_string: The connection string for server 2.

        Returns:
            A tuple containing database connections for server 1 and server 2.
        """

        server1_connection_parameters = DatabaseUtils.parse_connection_string(
            server1_connection_string
        )
        server2_connection_parameters = DatabaseUtils.parse_connection_string(
            server2_connection_string
        )

        return (
            mysql.connector.connect(**server1_connection_parameters),
            mysql.connector.connect(**server2_connection_parameters),
        )


