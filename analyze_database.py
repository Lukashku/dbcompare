from database_utils import DatabaseUtils
from wordpress_analyze import WordpressAnalyze

class AnalyzeDatabase:

    def __init__(self, cursor1, cursor2, args):
        self.cursor1 = cursor1
        self.cursor2 = cursor2
        self.args = args
    

    def underline_text(self, text):
        return ''.join([c + '\u0332' for c in text])

    def compare_tables(self):

        table_list_1 = DatabaseUtils.get_table_names(self.cursor1, self.args['database'])

        print(f"Server 1, database {self.args['database']} contains {len(DatabaseUtils.get_table_names(self.cursor1, self.args['database']))} tables")
        if self.cursor2:
            table_list_2 = DatabaseUtils.get_table_names(self.cursor2, self.args['database'])
            print(f"Server 2, database {self.args['database']} contains {len(DatabaseUtils.get_table_names(self.cursor2, self.args['database']))} tables")

            diff_1 = list(set(table_list_1) - set(table_list_2))
            diff_2 = list(set(table_list_2) - set(table_list_1))

            if diff_1:
                print("\n" + "-" * 50)
                print(f"\033[1mTables in {self.args['database']} on server 1 but not on server 2:\033[0m")
                print("-" * 50)
                for x in diff_1:
                    print(x)
            if diff_2:
                print("\n" + "-" * 50)
                print(f"\033[1mTables in {self.args['database']} on server 1 but not on server 2:\033[0m")
                print("-" * 50)
                for x in diff_2:
                    print(x)
            if not diff_1 and not diff_2:
                print(f"\nAll table names in {self.args['database']} on server 1 and server 2 are the same")
            if diff_1 and not diff_2:
                print(f"\nAll table names in {self.args['database']} on server 2 are in server 1.")
            if diff_2 and not diff_1:
                print(f"\nAll table names in {self.args['database']} on server 1 are in server 2.")
            
    def check_user_tables(self):
            user_table_names = [
        "users",
        "accounts",
        "logins",
        "members",
        "customers",
        "employees",
        "clients",
        "customers_info",
        "user_info",
        "user_data",
        "user_details",
        "user_credentials",
        "user_auth",
        "profiles",
        "user_profiles",
        "user_accounts",
        "authentications",
        "identities",
        "access_data",
        "security_info",
        "wp_users"
    ]
            user_tables_1 = [x for x in DatabaseUtils.get_table_names(self.cursor1, self.args['database']) if x in user_table_names]
            print(f"Server 1, potential user tables in database {self.args['database']} are: {user_tables_1}")
            if self.cursor1 and self.cursor2:
                user_tables_2 = [x for x in DatabaseUtils.get_table_names(self.cursor2, self.args['database']) if x in user_table_names]
                print(f"Server 2, potential user tables in database {self.args['database']} are: {user_tables_2}")
                self.dump_potential_users(user_tables_1, user_tables_2)
            
    def print_row(self, columns, row):
        for column, value in zip(columns, row):
            print(f"{column}: {value}")
        print("\n")

    def dump_potential_users(self, user_tables_1, user_tables_2=None):
        if "wp_users" in user_tables_1:
            cursor2 = self.cursor2 if user_tables_2 and "wp_users" in user_tables_2 else None
            WordpressAnalyze(self.cursor1, self.args['database'], cursor2).wp_users()
        else:
            for table in user_tables_1:
                self.cursor1.execute(f"SELECT * FROM {table}")
                rows = self.cursor1.fetchall()
                columns = [column[0] for column in self.cursor1.description]
                if rows:
                    print(f"\n{table} contains {len(rows)} rows")
                    print(f"First 5 rows of {table}:")
                    for row in rows[:5]:
                        self.print_row(columns, row)

            if user_tables_2:
                for table in user_tables_2:
                    self.cursor2.execute(f"SELECT * FROM {table}")
                    rows = self.cursor2.fetchall()
                    columns = [column[0] for column in self.cursor2.description]
                    if rows:
                        print(f"\n{table} contains {len(rows)} rows")
                        print(f"First 5 rows of {table}:")
                        for row in rows[:5]:
                            self.print_row(columns, row)

    def check_privileges(self):
        self.cursor1.execute("SHOW GRANTS FOR CURRENT_USER")
        privileges = self.cursor1.fetchall()
        for privilege in privileges:
            print(privilege)


    def main(self):

        self.compare_tables()
        self.check_user_tables()
        self.check_privileges()