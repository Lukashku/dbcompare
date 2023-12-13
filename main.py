import argparse
import logging

from common_data_remover import CommonDataRemover
from database_utils import DatabaseUtils

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def compare_databases(server1_connection_string, server2_connection_string, args):
    """
    Compares and removes common data between two databases.

    Args:
        server1_connection_string: The connection string for server 1.
        server2_connection_string: The connection string for server 2.
        args: An object containing parsed command-line arguments.
    """

    conn1, conn2 = DatabaseUtils.connect_to_databases(
        server1_connection_string, server2_connection_string
    )

    try:
        with conn1.cursor() as cursor1, conn2.cursor() as cursor2:
            CommonDataRemover.remove_common_data(
                cursor1, cursor2, args, logger=logger
            )
    finally:
        conn1.commit()
        conn1.close()
        conn2.commit()
        conn2.close()


def main():
    parser = argparse.ArgumentParser(description="Compares and removes common data between two MySQL databases.")
    parser.add_argument(
        "--server1",
        required=True,
        help="Connection string for server1, e.g., user:password@host:port",
    )
    parser.add_argument(
        "--server2",
        required=True,
        help="Connection string for server2, e.g., user:password@host:port",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--status-key",
        default="s",
        help="Key to trigger status update (default is \"s\")",
    )
    parser.add_argument("--database", help="Databases to compare, each specified separately")
    parser.add_argument("--table", help="Optional: Specify a specific table to compare")
    parser.add_argument("--exact", action="store_true", help="Enable exact matching, including the id column")
    parser.add_argument("--exclude", "-xt", dest="exclude", help="Tables to exclude, separated by commas")
    parser.add_argument("-L", "--list", action="store_true", help="List databases from each server and exit")
    parser.add_argument("--log-file", help="Specify a log file path")

    args = parser.parse_args()

    if args.list:
        server1_databases = DatabaseUtils.connect_and_list_databases(args.server1)
        server2_databases = DatabaseUtils.connect_and_list_databases(args.server2)

        logger.info("Server 1 Databases:")
        for database in server1_databases:
            logger.info(f"- {database}")

        logger.info("Server 2 Databases:")
        for database in server2_databases:
            logger.info(f"- {database}")

        return

    if not args.database:
        logger.error("Error: --database is required.")
        parser.print_help()
        sys.exit(1)

    compare_databases(args.server1, args.server2, args)


if __name__ == "__main__":
    main()

