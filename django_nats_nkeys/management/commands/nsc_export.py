from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser

from django_nats_nkeys.settings import nats_nkeys_settings
from django_nats_nkeys.services import nsc_export


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dir",
            type=str,
            help="Export nkeys to path",
            default=nats_nkeys_settings.NATS_NKEYS_EXPORT_DIR,
        )

    def handle(self, *args, **kwargs):
        indir = kwargs.get("dir")
        nsc_export(indir)
