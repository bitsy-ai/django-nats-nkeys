from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

User = get_user_model()


# class TestCommand(TestCase):
#     def setUp(self) -> None:
#         super().setUp()
#         self.user = User.objects.create(
#             email="admin@test.com", password="testing1234", is_superuser=True
#         )

#     def test_secret_sync(self):
#         out = StringIO()
#         call_command("nsc_push", stdout=out)
#         assert "Created TurnSecret" in out.getvalue()

#     def test_admin_sync(self):
#         out = StringIO()
#         call_command("nsc_pull",stdout=out)
#         assert f"Created TurnAdmin object ({self.user.id})" in out.getvalue()

#     def test_user_sync(self):
#         out = StringIO()
#         call_command("", "turn_user", stdout=out)
#         assert f"Created TurnUser object ({self.user.id})" in out.getvalue()
