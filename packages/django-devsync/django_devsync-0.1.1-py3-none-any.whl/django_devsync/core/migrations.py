from pathlib import Path

from .utils import confirm


def get_migration_files() -> list[Path]:
    """
    Recursively find all Django migration files in the project directory.

    Prompts the user for the project root path (defaults to '.').
    Skips common excluded directories like 'venv' and 'site-packages'.
    Returns a list of paths to migration `.py` and `.pyc` files (excluding __init__.py).
    """

    print("\n🔍 Scanning for migration files to delete...")

    root_path = input("Enter project root path [default='.']: ").strip() or "."
    base_path = Path(root_path)

    migration_files = []
    for migrations_dir in base_path.rglob("migrations"):
        if any(
            excluded in str(migrations_dir)
            for excluded in ["venv", "site-packages"]
        ):
            continue

        for file in migrations_dir.glob("*.py"):
            if file.name != "__init__.py":
                migration_files.append(file)
        for file in migrations_dir.glob("*.pyc"):
            migration_files.append(file)

    return migration_files


def delete_migrations() -> None:
    """
    Delete all found Django migration files after user confirmation.

    Prints a list of files to be deleted, asks the user to confirm,
    and deletes them. If no files are found, exits early.
    """

    migration_files = get_migration_files()
    if not migration_files:
        print("✅ No migration files found.")
        return

    print("\n🚨 The following migration files will be deleted:")
    for file in migration_files:
        print(f"  - {file}")

    if not confirm():
        return

    for file in migration_files:
        file.unlink()
    print("✅ All migration files deleted.")
