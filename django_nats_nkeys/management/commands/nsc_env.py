import subprocess
import os

from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser

from django_nats_nkeys.settings import nats_nkeys_settings


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:

        parser.add_argument(
            "--name",
            type=str,
            help="Name of operator",
            default=nats_nkeys_settings.NATS_NKEYS_OPERATOR_NAME,
        )

    def handle(self, *args, **kwargs):
        # print env
        name = kwargs.get("name")

        result = subprocess.run(
            f"nsc env -o {name}", capture_output=True, encoding="utf8", shell=True
        )

        if result.stderr:
            self.stderr.write(result.stderr)

        if result.stdout:
            self.stdout.write(result.stdout)
        result.check_returncode()
