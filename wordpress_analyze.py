import sys

class WordpressAnalyze:
    def __init__(self, cursor1, args, cursor2=None):
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
    def wp_users(self):
        # Select all rows from the wp_users table
        self.cursor1.execute("SELECT * FROM wp_users")
        users1 = self.cursor1.fetchall()

        # Assume 'user_login' is the first field and 'user_pass' is the second field in the tuples returned by fetchall()
        user_login_index = 1
        user_pass_index = 2

        # Convert the results to a dictionary with user_login as the key
        users1_dict = {user[user_login_index]: user for user in users1}

        if self.cursor2:
            self.cursor2.execute("SELECT * FROM wp_users")
            users2 = self.cursor2.fetchall()

            # Convert the results to a dictionary with user_login as the key
            users2_dict = {user[user_login_index]: user for user in users2}

            # Find any new or missing users
            new_users = set(users1_dict.keys()) - set(users2_dict.keys())
            missing_users = set(users2_dict.keys()) - set(users1_dict.keys())

            # Find users who have changed their passwords
            changed_password_users = {user_login for user_login in users1_dict if user_login in users2_dict and users1_dict[user_login][user_pass_index] != users2_dict[user_login][user_pass_index]}

            # Print all data for new, missing, or changed password users
            if new_users:
                print("\n" + "-" * 50)
                print("Newly added users:")
                print("-" * 50)
                for user_login in new_users:
                    user = users1_dict[user_login]
                    print(f"New user: {user[1]}\nPassHash= {user[2]}\nName= {user[3]}\nEmail={user[4]}\nuser_registered= {user[6]}\n")
            if missing_users:
                print("\n" + "-" * 50)
                print("Users who have been deleted:")
                print("-" * 50)
                for user_login in missing_users:
                    user = users2_dict[user_login]
                    print(f"Deleted user: {user[1]}\nPassHash= {user[2]}\nName= {user[3]}\nEmail={user[4]}\nuser_registered= {user[6]}\n")
            if changed_password_users:
                print("\n" + "-" * 50)
                print("Users who changed their passwords:")
                print("-" * 50)
                for user_login in changed_password_users:
                    user = users1_dict[user_login]
                    print(f"User changed password: {user[1]}\nOld PassHash= {users2_dict[user_login][2]}\nNew PassHash= {user[2]}\nName= {user[3]}\nEmail={user[4]}\nuser_registered= {user[6]}\n")
                
        else:
            # Print all data for users
            for user_login, user in users1_dict.items():
                print(f"User: {user[1]}\nPassHash= {user[2]}\nName= {user[3]}\nEmail={user[4]}\nuser_registered= {user[6]}\n")

    def wp_options(self):
        # Query the wp_options table in both databases
        self.cursor1.execute("SELECT option_name, option_value FROM wp_options")
        options1 = {row[0]: row[1] for row in self.cursor1.fetchall()}

        self.cursor2.execute("SELECT option_name, option_value FROM wp_options")
        options2 = {row[0]: row[1] for row in self.cursor2.fetchall()}

        # Convert the lists to sets for efficient operations
        options1_set = set(options1.keys())
        options2_set = set(options2.keys())

        # Find the option_values that occur in both databases
        common_options = options1_set.intersection(options2_set)

        # Find the option_values that are in server2 but not in server1 (deleted)
        deleted_options = options2_set.difference(options1_set)

        # Find the option_values that are in server1 but not in server2 (new)
        new_options = options1_set.difference(options2_set)

        # Print the results
        # print(f"Common options: {common_options}")
        # print(f"Deleted options: {deleted_options}")
        # print(f"New options: {new_options}")

        # Check if any of the important options are common and if their values have changed
        important_options = [
            {"name": "acf_pro_license", "description": "ACF Pro License Key"},
            {"name": "active_plugins", "description": "Serialized array of active plugins"},
            {"name": "admin_email", "description": "Site administrator's email address"},
            {"name": "autoptimize_version", "description": "Autoptimize plugin version"},
            {"name": "external_updates-tablepress-responsive-tables", "description": "TablePress Responsive Tables plugin updates"},
            {"name": "fs_active_plugins", "description": "Serialized array of active plugins from Filesystem API"},
            {"name": "home", "description": "WordPress site URL"},
            {"name": "siteurl", "description": "Home URL"},
            {"name": "limit_login_retries", "description": "Login retries configuration"},
            {"name": "recently_edited", "description": "Recently edited files"},
            {"name": "redirection_options", "description": "Redirection plugin options"},
            {"name": "site_logo", "description": "Site logo information"},
            {"name": "wordfence_lastSyncAttackData", "description": "Wordfence last synchronization data"},
            {"name": "wordfence_version", "description": "Wordfence plugin version"},
            {"name": "wpseo", "description": "Yoast SEO plugin settings"},
            {"name": "wpseo_premium", "description": "Yoast SEO Premium settings"},
            {"name": "wsal_disable-daily-summary", "description": "WP Security Audit Log plugin daily summary email"},
            {"name": "wsal_disable-widgets", "description": "WP Security Audit Log plugin widget settings"},
            {"name": "yoast_migrations_free", "description": "Yoast SEO Free migrations status"},
            {"name": "yoast_migrations_premium", "description": "Yoast SEO Premium migrations status"},
            {"name": "wpseo-premium-redirects-base", "description": "Yoast SEO Premium redirects base settings"},
            {"name": "wpseo-premium-redirects-export-plain", "description": "Yoast SEO Premium redirects export settings"},
        ]
        for option in important_options:
            if option["name"] in common_options and options1[option["name"]] != options2[option["name"]]:
                print(f"Option name: {option['name']}\nDescription: {option['description']}\nOld value: {options2[option['name']]}\nNew value: {options1[option['name']]}\n")

            # Check if any of the important options are new
            if option["name"] in new_options:
                print(f"New Option Name: {option['name']}\nDescription: {option['description']}\nValue: {options1[option['name']]}\n")

            # Check if any of the important options have been deleted
            if option["name"] in deleted_options:
                print(f"Deleted Option Name: {option['name']}\nDescription: {option['description']}\nValue: {options2[option['name']]}\n")

    def main(self):

        if self.args['wp_users']:
            self.wp_users()
        elif self.args['wp_options']:
            self.wp_options()
        else:
            print("Error: No command specified.")
            self.wordpress_parser.print_help()
            sys.exit(1)