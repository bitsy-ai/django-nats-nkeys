from io import StringIO
import tempfile
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

User = get_user_model()


class TestCommand(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create(
            email="admin@test.com", password="testing1234", is_superuser=True
        )

    def test_nsc_init(self):
        out = StringIO()

        name = "TestOperator"
        with tempfile.TemporaryDirectory() as tmp_path:
            expected = f"[ OK ] wrote server configuration to `{tmp_path}/{name}.conf`"
            call_command("nsc_init", dir=str(tmp_path), name=name,stdout=out, stderr=out)
            assert True
            print(out.getvalue())
            assert expected in out.getvalue()
