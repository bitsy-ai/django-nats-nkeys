from django.test import TestCase
from django.contrib.auth import get_user_model
from django_nats_nkeys.services import (
    create_nats_account_org,
    create_nats_app,
    nsc_generate_creds,
)
from coolname import generate_slug

User = get_user_model()


class TestServices(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create(
            email="admin@test.com", password="testing1234", is_superuser=False
        )
        self.org = create_nats_account_org(self.user)
        self.app = create_nats_app(self.user, self.org)

    def test_create_nats_app(self):
        assert self.org.name == self.org.json.get("name")
        app = create_nats_app(self.user, self.org)
        assert app.organization == self.org

    def test_nsc_generate_creds(self):
        creds = nsc_generate_creds(self.org, self.app)

        assert ("-----BEGIN NATS USER JWT-----") in creds
        assert ("------END NATS USER JWT------") in creds
        assert ("-----BEGIN USER NKEY SEED-----") in creds
        assert ("------END USER NKEY SEED------") in creds
