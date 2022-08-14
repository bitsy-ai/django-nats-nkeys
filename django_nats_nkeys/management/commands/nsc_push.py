from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser

from django_nats_nkeys.services import nsc_push


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--account",
            help="Push a specific account. If not provided, push --all will be executed",
            required=False,
        )

        parser.add_argument(
            "--force",
            help="Overwrite existing keys in --dir",
            default=False,
            action="store_true",
        )

    def handle(self, *args, **kwargs):
        force = kwargs.get("force")
        account = kwargs.get("account")
        nsc_push(account=account, force=force)
