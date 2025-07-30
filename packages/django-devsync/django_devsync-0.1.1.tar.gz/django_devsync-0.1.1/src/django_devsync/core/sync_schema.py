from django.core.management import call_command

from .utils import confirm


def run_sync() -> None:
    """
    Run Django's makemigrations and migrate commands.

    Asks for user confirmation before proceeding. If confirmed,
    it creates new migrations and applies them to sync the database
    schema with current models.
    """

    print("\nRunning makemigrations + migrate...")
    if not confirm():
        return

    call_command("makemigrations", interactive=False)
    call_command("migrate", interactive=False)
    print("DB schema synced with models.\n")
