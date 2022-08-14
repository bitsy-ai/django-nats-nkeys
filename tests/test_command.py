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

    def test_nsc_push(self):
        # test non-zero exits
        call_command("nsc_push", "--force")
        call_command("nsc_push")

    def test_nsc_pull(self):
        call_command("nsc_pull", "--force")
        call_command("nsc_pull")

    def test_nsc_operator_jwt(self):

        with tempfile.NamedTemporaryFile() as f:
            filename = f.name
        # exit context and delete file. nsc doesn't have an --overwrite flag for nsc describe... command will fail if file exists
        call_command("nsc_operator_jwt", "--export", f"{f.name}")
        call_command("nsc_operator_jwt", "--import", f"{f.name}")
