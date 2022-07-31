import os

from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser

from django_nats_nkeys.settings import nats_nkeys_settings
from django_nats_nkeys.services import nsc_init_operator


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:

        parser.add_argument(
            "--name",
            type=str,
            help="Name of operator",
            default=nats_nkeys_settings.NATS_NKEYS_OPERATOR_NAME,
        )
        parser.add_argument(
            "--outdir",
            type=str,
            help="Output signing key for offline/cold storage",
            default=nats_nkeys_settings.NATS_NKEYS_EXPORT_DIR,
        )

    def handle(self, *args, **kwargs):
        name = kwargs.get("name")
        outdir = kwargs.get("outdir")
        filename = os.path.join(outdir, f"{name}.conf")
        try:
            os.remove(filename)
            self.stdout.write(self.style.SUCCESS(f"Deleted {filename}"))
        except FileNotFoundError:
            self.stderr.write(self.style.NOTICE(f"File not found {filename}"))
