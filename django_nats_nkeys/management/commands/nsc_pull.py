from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser

from django_nats_nkeys.services import nsc_pull


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        nsc_pull()
