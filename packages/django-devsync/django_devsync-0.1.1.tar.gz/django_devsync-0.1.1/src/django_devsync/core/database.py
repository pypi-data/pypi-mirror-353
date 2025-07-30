import os

from django.db import connection

from .utils import confirm


def reset_db():
    """
    Resets the database schema depending on the engine.

    - PostgreSQL: Drops and recreates the `public` schema.
    - MySQL: Drops all tables.
    - SQLite: Deletes the `.sqlite3` file.

    Raises:
        RuntimeError: If the database engine is unsupported or connection fails.
    """

    from django.conf import settings

    engine = settings.DATABASES["default"]["ENGINE"]

    if "sqlite" in engine:
        _handle_sqlite(settings)

    elif "postgresql" in engine:
        _handle_postgresql()

    elif "mysql" in engine:
        _handle_mysql()

    else:
        raise NotImplementedError(
            f"DB engine '{engine}' not supported for reset."
        )


def _handle_sqlite(settings):
    db_path = settings.DATABASES["default"]["NAME"]
    if not os.path.isfile(db_path):
        print("No SQLite DB file found to delete.")
        return

    print(f"\n🚨 The {db_path} will be deleted:")
    if not confirm():
        return

    os.remove(db_path)
    print(f"Deleted SQLite DB file at: {db_path}")
    return


def _handle_mysql():
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"\nRemoving tables: {tables}")
        if not confirm():
            return

        print("Disabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

        print("Dropping tables...")
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS `{table}`;")

        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"After reset, tables: {tables}")

        print("Re-enabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

    print("✅ Dropped all tables in MySQL")


def _handle_postgresql():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname='public';"
        )

        print("\nRemoving tables:", cursor.fetchall())
        if not confirm():
            return

        cursor.execute("DROP SCHEMA public CASCADE;")
        cursor.execute("CREATE SCHEMA public;")

        cursor.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname='public';"
        )
        print("After reset, tables:", cursor.fetchall())

    print("Dropped and recreated public schema in PostgreSQL")
