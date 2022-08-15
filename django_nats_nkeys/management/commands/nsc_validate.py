from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser

from django_nats_nkeys.services import nsc_validate


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--account",
            help="Push a specific account. If not provided, push --all will be executed",
            required=False,
        )

    def handle(self, *args, **kwargs):
        account_name = kwargs.get("account_name")
        nsc_validate(account_name=account_name)
