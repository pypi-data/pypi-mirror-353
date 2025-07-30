"""
Main entry point for django-devsync CLI.

This script orchestrates the core operations:
- Deleting migration files
- Resetting the database
- Running makemigrations and migrate

All operations are safe for development environments only.
NEVER use this on production systems.

Functions:
    main(): Parses CLI args, sets up Django, and executes selected operations.
"""

import os
import sys

from .core import (
    setup_django,
    check_debug,
    delete_migrations,
    reset_db,
    run_sync,
)
from .args import parse_arguments, describe_plan


def main():
    """
    Run the django-devsync CLI tool.

    - Adds current working directory to sys.path for dynamic Django setup
    - Parses CLI arguments
    - Displays planned operations
    - Initializes Django and checks DEBUG mode
    - Executes selected operations (or all if no flags are passed)

    Raises:
        RuntimeError: If run in non-debug (production) mode.
    """

    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    print(
        "🛑🛑🛑 DON'T USE THIS TOOL ON PRODUCTION 🛑🛑🛑\n"
        "🚧 django-devsync is for development use only!\n"
    )

    args = parse_arguments()
    run_all = not any(vars(args).values())

    describe_plan(args)
    setup_django()
    check_debug()

    if run_all or args.delete_migrations:
        delete_migrations()
    if run_all or args.reset_db:
        reset_db()
    if run_all or args.run_sync:
        run_sync()
