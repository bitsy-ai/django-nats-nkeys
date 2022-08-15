import tempfile
import os
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from coolname import generate_slug

from django_nats_nkeys.models import NatsOrganizationUser
from django_nats_nkeys.services import create_organization

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

        with tempfile.TemporaryDirectory() as d:
            operator_jwt = os.path.join(d, "operator.jwt")
            call_command("nsc_operator_jwt", "--export", operator_jwt)
            call_command("nsc_operator_jwt", "--import", operator_jwt, "--force")

            # create NATS account
            org_name = generate_slug(3)
            org = create_organization(
                self.user,
                org_name,
                org_user_defaults={"is_admin": True},
            )
            # test account jwt
            account_jwt = os.path.join(d, "account.jwt")
            call_command("nsc_account_jwt", "--export", account_jwt, "--name", org.name)
            import pdb

            pdb.set_trace()
            call_command("nsc_account_jwt", "--import", account_jwt, "--force")

            # test user jwt
            org_user = NatsOrganizationUser.objects.get(user=self.user)

            user_jwt = os.path.join(d, "user.jwt")
            call_command(
                "nsc_user_jwt", "--export", user_jwt, "--name", org_user.app_name
            )
            call_command("nsc_user_jwt", "--import", user_jwt, "--force")

    def nsc_validate(self):
        call_command("nsc_valicate")
