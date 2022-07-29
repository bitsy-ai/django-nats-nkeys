
import subprocess
import os

from click import BaseCommand
from django.core.management.base import BaseCommand, CommandParser

from django_nats_nkeys.settings import nats_nkeys_settings

class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        
        parser.add_argument('--name',  type=str, help="Name of operator", default=nats_nkeys_settings.NATS_NKEYS_OPERATOR_NAME)
        parser.add_argument('--server',   type=str, help="Nats server URI", default=nats_nkeys_settings.NATS_SERVER_URI)
        parser.add_argument('--dir', type=str, help="Output generated config to dir", default=".nats/")

    def handle(self, *args, **kwargs):
        print(kwargs)
        name = kwargs.get("name")
        server = kwargs.get("server")
        outdir = kwargs.get("dir")


        # create operator with name
        result = subprocess.run(
            f"nsc init --name {name}", capture_output=True, encoding="utf8", shell=True, check=True)
        if result.stderr:
            self.stderr.write(result.stderr)

        if result.stdout:
            self.stdout.write(result.stdout)
        result.check_returncode()

        # print env
        result = subprocess.run(
            f"nsc env", capture_output=True, encoding="utf8", shell=True, check=True)

        if result.stderr:
            self.stderr.write(result.stderr)

        if result.stdout:
            self.stdout.write(result.stdout)
        result.check_returncode()

        # set operator context and generate config
        filename = os.path.join(outdir, f"{name}.conf")
        result = subprocess.run(
            f"nsc generate config --nats-resolver --config-file {filename}",capture_output=True, encoding="utf8", shell=True)
        
        if result.stderr:
            self.stderr.write(result.stderr)

        if result.stdout:
            self.stdout.write(result.stdout)
