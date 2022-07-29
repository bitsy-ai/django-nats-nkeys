

from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        
        parser.add_argument('email',  required=True, type=str, help="Organization owner email")