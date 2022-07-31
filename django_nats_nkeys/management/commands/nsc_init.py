import subprocess
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
            "--server",
            type=str,
            help="Nats server URI",
            default=nats_nkeys_settings.NATS_SERVER_URI,
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
        server = kwargs.get("server")
        nsc_init_operator(name, outdir, server, stdout=self.stdout, stderr=self.stderr)
