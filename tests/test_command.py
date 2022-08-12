from io import StringIO
import tempfile
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from coolname import generate_slug

User = get_user_model()


class TestCommand(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create(
            email="admin@test.com", password="testing1234", is_superuser=True
        )

    def test_nsc_import_export(self):
        call_command("nsc_export")
        call_command("nsc_import")
