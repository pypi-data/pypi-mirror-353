import argparse


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the devsync tool.

    Returns:
        argparse.Namespace: Parsed command-line arguments with flags for
        deleting migrations, resetting the DB, and syncing schema.
    """

    parser = argparse.ArgumentParser(
        description="Sync your Django dev DB schema like TypeORM's synchronize=true"
    )
    parser.add_argument(
        "--delete_migrations",
        action="store_true",
        help="Delete all migration files",
    )
    parser.add_argument(
        "--reset_db",
        action="store_true",
        help="Drop all DB tables or schemas",
    )
    parser.add_argument(
        "--run_sync",
        action="store_true",
        help="Run makemigrations and migrate",
    )

    args = parser.parse_args()
    return args


def describe_plan(args: argparse.Namespace) -> None:
    """
    Print a summary of which operations will be performed based on CLI arguments.

    Args:
        args (argparse.Namespace): Parsed arguments from parse_arguments().
    """

    if not any(vars(args).values()):
        print("No specific flags passed — running ALL steps:")
        print("  - Deleting all migrations")
        print("  - Resetting the database")
        print("  - Running makemigrations and migrate\n")

        return

    print("Planned Operations:")
    if args.delete_migrations:
        print("  - Delete all migration files")
    if args.reset_db:
        print("  - Drop/reset the database")
    if args.run_sync:
        print("  - Run makemigrations + migrate")
    print()
