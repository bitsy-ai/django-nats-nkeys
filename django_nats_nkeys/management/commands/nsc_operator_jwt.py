from multiprocessing.sharedctypes import Value
from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser

from django_nats_nkeys.settings import nats_nkeys_settings
from django_nats_nkeys.services import run_nsc_and_log_output


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:

        parser.add_argument(
            "--import",
            type=str,
            help="Import operator from operator.jwt",
        )
        parser.add_argument(
            "--export",
            type=str,
            help="Create operator.jwt",
        )
        parser.add_argument(
            "--name",
            type=str,
            help="Operator name",
            default=nats_nkeys_settings.NATS_NKEYS_OPERATOR_NAME,
        )

    def handle(self, *args, **kwargs):
        importf = kwargs.get("import")
        exportf = kwargs.get("export")
        name = kwargs.get("name")
        if importf is None and exportf is None:
            raise ValueError("One of --import|export is required")
        if importf is not None and exportf is not None:
            raise ValueError("Please specify one of --import|export (received both)")

        if importf is not None:
            run_nsc_and_log_output(["nsc", "add", "operator", "-u", importf])
            self.stdout.write(
                self.style.SUCCESS(f"Success! Imported from JWT {importf}")
            )
        if exportf is not None:
            run_nsc_and_log_output(
                ["nsc", "describe", "operator", "--raw", "--output-file", exportf]
            )
            self.stdout.write(
                self.style.SUCCESS(f"Success! Wrote operator JWT to {importf}")
            )