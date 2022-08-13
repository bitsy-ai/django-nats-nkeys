# import subprocess
# import pytest
# from django.contrib.auth import get_user_model
# from django.core.management import call_command
# from django.test import TestCase
# from coolname import generate_slug

# User = get_user_model()


# class TestCommand(TestCase):
#     def setUp(self) -> None:
#         super().setUp()
#         self.user = User.objects.create(
#             email="admin@test.com", password="testing1234", is_superuser=True
#         )

#     def test_nsc_import_export(self):
#         # test non-zero exits
#         call_command("nsc_export", "--force")
#         call_command("nsc_import")
#         # test raises error if force flag not provided
#         with pytest.raises(subprocess.CalledProcessError):
#             call_command("nsc_export")

#     def test_nsc_pull(self):
#         call_command("nsc_pull")
