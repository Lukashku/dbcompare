import mysql.connector 

class WordpressAnalyze:
    def __init__(self, cursor1, cursor2, args):
        self.cursor1 = cursor1
        self.cursor2 = cursor2
        self.args = args

        # Initialize any necessary variables or resources here
        self.wp_basic_tables = [
            "wp_posts",
            "wp_comments",
            "wp_links",
            "wp_options",
            "wp_postmeta",
            "wp_terms",
            "wp_term_taxonomy",
            "wp_term_relationships",
            "wp_termmeta",
            "wp_users",
            "wp_usermeta",
            "wp_terms"
        ]
    def analyze_basic(self):
        # Select all rows from the wp_users table in both databases
        self.cursor1.execute("SELECT * FROM wp_users")
        users1 = self.cursor1.fetchall()

        self.cursor2.execute("SELECT * FROM wp_users")
        users2 = self.cursor2.fetchall()

        # Assume 'user_login' is the first field and 'user_pass' is the second field in the tuples returned by fetchall()
        user_login_index = 1
        user_pass_index = 2

        # Convert the results to dictionaries with user_login as the key
        users1_dict = {user[user_login_index]: user for user in users1}
        users2_dict = {user[user_login_index]: user for user in users2}

        # Find any new or missing users
        new_users = set(users1_dict.keys()) - set(users2_dict.keys())
        missing_users = set(users2_dict.keys()) - set(users1_dict.keys())

        # Find users who have changed their passwords
        changed_password_users = {user_login for user_login in users1_dict if user_login in users2_dict and users1_dict[user_login][user_pass_index] != users2_dict[user_login][user_pass_index]}

        # Print all data for new, missing, or changed password users
        for user_login in new_users:
            user = users1_dict[user_login]
            print(f"New user: {user[1]}\nPassHash= {user[2]}\nName= {user[3]}\nEmail={user[4]}\nuser_registered= {user[6]}\n")

        for user_login in missing_users:
            user = users2_dict[user_login]
            print(f"Deleted user: {user[1]}\nPassHash= {user[2]}\nName= {user[3]}\nEmail={user[4]}\nuser_registered= {user[6]}\n")

        for user_login in changed_password_users:
            user = users1_dict[user_login]
            print(f"User changed password: {user[1]}\nOld PassHash= {users2_dict[user_login][2]}\nNew PassHash= {user[2]}\nName= {user[3]}\nEmail={user[4]}\nuser_registered= {user[6]}\n")
