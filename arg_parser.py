import argparse

def get_args():

    main_parser = argparse.ArgumentParser(description='Compare and remove common data between two MySQL databases.')
    subparsers = main_parser.add_subparsers(dest='command')
    # Create the parser for the "main" command
    main_parser_main = subparsers.add_parser('main', help='Main command')
    main_parser_main.add_argument('--server1', required=True, help='Connection string for server1, e.g., user:password@host:port')
    main_parser_main.add_argument('--server2', required=False, help='Connection string for server2, e.g., user:password@host:port')
    main_parser_main.add_argument('--verbose', action='store_true', help='Enable verbose output')
    main_parser_main.add_argument('--database', '-db', required=True, help='Databases to compare, each specified separately')
    main_parser_main.add_argument('--table', '-t', help='Optional: Specify a specific table to compare')
    main_parser_main.add_argument('--exact', action='store_true', help='Enable exact matching, including the id column')
    main_parser_main.add_argument('--exclude', '-xt', dest='exclude', help='Tables to exclude, separated by commas')
    main_parser_main.add_argument('--log', action='store_true', help='Enable logging')
    main_parser_main.add_argument('--log-output', default=None, help='The directory to output log files to')

    wordpress_parser = subparsers.add_parser('wordpress', help='Enable WordPress-specific analysis')
    wordpress_parser.add_argument('--basic', action='store_true', help='Perform basic WordPress analysis')
    wordpress_parser.add_argument('--wp-users', action='store_true', help='Analyzes the wp_users table')
    wordpress_parser.add_argument('--wp-options', action='store_true', help='Analyzes the wp_options table')

    # Subparser for the 'information' command
    info_parser = subparsers.add_parser('information', help='Fetch information about and/or query the database(s)')
    info_parser.add_argument('--server1', help='The first server')
    info_parser.add_argument('--server2', required=False, help='The second server (optional)')
    info_parser.add_argument('--database', '-db', help='The database')
    info_parser.add_argument('--sql-query', nargs='?', help='The query to execute (optional, only if --openai is passed)')
    info_parser.add_argument('--openai', action='store_true', help='Use OpenAI to generate the SQL query (Experimental)')
    info_parser.add_argument('--list', '-L', action='store_true', help='List databases from the specified server(s)')
    info_parser.add_argument('--tables', '-T', action='store_true', help='List tables from the specified database')

    return vars(main_parser.parse_args()), main_parser
    