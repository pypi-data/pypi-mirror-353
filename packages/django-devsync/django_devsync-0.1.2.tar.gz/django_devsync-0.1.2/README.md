# django-devsync

A tiny command-line tool that mimics `synchronize: true` from TypeORM — but for Django.

[![PyPI](https://img.shields.io/pypi/v/django-devsync)](https://pypi.org/project/django-devsync/)

**Strictly for development use. Never use in production.**

---

## What It Does

In early-stage development, database schemas change fast and migrations get messy. `django-devsync` helps you:

- **Delete all migration files**
- **Reset your local DB schema**
- **Run `makemigrations` and `migrate` from scratch**

All with a single command.

---

## Don't Use In Production 🛑

This tool **WILL destroy data** and has minimal safeguards.

---

## Installation

```bash
pip install django-devsync
```

---

## Usage

```bash
devsync --delete_migrations --reset_db --run_sync
```

or

```bash
python -m django_devsync --delete_migrations --reset_db --run_sync
```

If no flags are passed, it runs **all steps**.

### Flags

| Flag                  | Description                                                        |
| --------------------- | ------------------------------------------------------------------ |
| `--delete_migrations` | Delete all `.py` and `.pyc` files in `migrations/` directories     |
| `--reset_db`          | Drop all tables/schemas in your local DB (SQLite/PostgreSQL/MySQL) |
| `--run_sync`          | Run `makemigrations` and `migrate`                                 |

---

## Example

```bash
devsync
```

or

```bash
python -m django_devsync
```

Output:

```
No specific flags passed — running ALL steps:
• Deleting all migrations
• Resetting the database
• Running makemigrations and migrate

All done!

```

---

## Supported Databases

- SQLite
- MySQL
- PostgreSQL

> Uses Django's `DATABASES['default']['ENGINE']` to detect backend.

---

## How It Works

- Prompts for your `DJANGO_SETTINGS_MODULE` (unless set in env)
- Verifies `DEBUG=True` before proceeding
- Uses Django internals: `call_command("makemigrations")`, etc.
- Drops and recreates schemas/tables directly with SQL

---

## Contributions

Bug reports, feedback, and PRs are welcome. Stars are appreciated.

---

## License

MIT
