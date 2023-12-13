import mysql.connector
from database_utils import DatabaseUtils
from common_data_remover import CommonDataRemover

class DatabaseComparator:
    @staticmethod
    def compare_databases(cursor1, cursor2, database, table=None, exact=False, verbose=False, exclude=None):
        databases1 = DatabaseUtils.get_database_names(cursor1)
        databases2 = DatabaseUtils.get_database_names(cursor2)

        if exclude:
            databases1 = DatabaseUtils.exclude_databases(databases1, exclude)
            databases2 = DatabaseUtils.exclude_databases(databases2, exclude)

        for db1, db2 in zip(databases1, databases2):
            if db1 != db2:
                print(f"Warning: Mismatch in databases. {db1} in server1 does not match {db2} in server2.")
                continue

            cursor1.execute(f"USE {db1}")
            cursor2.execute(f"USE {db2}")

            tables1 = DatabaseUtils.get_table_names(cursor1, db1)
            tables2 = DatabaseUtils.get_table_names(cursor2, db2)

            for t1, t2 in zip(tables1, tables2):
                if table is None or (table and t1 == t2 and (table == t1 or table == t2)):
                    CommonDataRemover.remove_common_data(cursor1, cursor2, t1, db1, exact, verbose)

