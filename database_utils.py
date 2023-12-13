import re

class DatabaseUtils:
    @staticmethod
    def get_database_names(cursor):
        cursor.execute("SHOW DATABASES")
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def get_table_names(cursor, database):
        cursor.execute(f"USE {database}")
        cursor.execute("SHOW TABLES")
        return [row[0] for row in cursor.fetchall()]

    @staticmethod
    def exclude_databases(databases, exclude):
        return [db for db in databases if db not in exclude]

    @staticmethod
    def parse_connection_string(connection_string):
        match = re.match(r'([^:@]+)(?::([^@]+))?@([^:]+):(\d+)', connection_string)
        if match:
            user, password, host, port = match.groups()
            return user, password, host, int(port)
        else:
            raise ValueError("Invalid connection string format")

    # Add the table_exists method to DatabaseUtils
    @staticmethod
    def table_exists(cursor, table_name, database):
        cursor.execute("SHOW TABLES IN {}".format(database))
        tables = [row[0] for row in cursor.fetchall()]
        return table_name in tables

