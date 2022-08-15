from multiprocessing.sharedctypes import Value
from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser

from django_nats_nkeys.services import run_nsc_and_log_output


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:

        parser.add_argument(
            "--import",
            type=str,
            help="Import account from .jwt",
        )
        parser.add_argument(
            "--export",
            type=str,
            help="Create operator.jwt",
        )
        parser.add_argument(
            "--name",
            type=str,
            help="Account name",
        )
        parser.add_argument("--force", action="store_true", default=False)

    def handle(self, *args, **kwargs):
        importf = kwargs.get("import")
        force = kwargs.get("force")
        exportf = kwargs.get("export")
        name = kwargs.get("name")

        if importf is None and exportf is None:
            raise ValueError("One of --import|export is required")
        if importf is not None and exportf is not None:
            raise ValueError("Please specify one of --import|export (received both)")

        if exportf is not None and name is None:
            raise ValueError("--name is required")

        if importf is not None:
            cmd = ["nsc", "import", "account", "--file", importf]
            if force is True:
                cmd += ["--force"]
            run_nsc_and_log_output(cmd)
            self.stdout.write(
                self.style.SUCCESS(f"Success! Imported from JWT {importf}")
            )

        if exportf is not None:
            cmd = [
                "nsc",
                "describe",
                "account",
                "--name",
                name,
                "--raw",
                "--output-file",
                exportf,
            ]
            self.stdout.write(
                self.style.SUCCESS(f"Success! Output account JWT to {exportf}")
            )
