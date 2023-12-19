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

        for db1 in databases1:
            if db1 not in databases2:
                print(f"Warning: Database {db1} in server1 does not exist in server2.")
                continue

            cursor1.execute(f"USE {db1}")
            cursor2.execute(f"USE {db1}")

            tables1 = DatabaseUtils.get_table_names(cursor1, db1)
            tables2 = DatabaseUtils.get_table_names(cursor2, db1)

            for t1 in tables1:
                if t1 not in tables2:
                    print(f"Warning: Table {t1} in database {db1} in server1 does not exist in server2.")
                    continue

                if table is None or (table and table == t1):
                    CommonDataRemover.remove_common_data(cursor1, cursor2, t1, db1, exact, verbose)

    @staticmethod
    def compare_databases_with_args(cursor1, cursor2, args):
        all_tables = [x.strip() for x in args['table'].split(',')] if args.get('table') else DatabaseUtils.get_table_names(cursor1, args['database'])
        exclude_tables = [x.strip() for x in args['exclude'].split(',')] if args.get('exclude') else []
        tables = [x for x in all_tables if x not in exclude_tables]
        print(tables)

        print(exclude_tables)
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
        print("Comparison complete.")