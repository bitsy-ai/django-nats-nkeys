from django.test import TestCase
from django.contrib.auth import get_user_model
from django_nats_nkeys.services import (
    create_nats_account_org,
    create_nats_app,
    nsc_generate_creds,
)
from django_nats_nkeys.models import AbstractNatsApp
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
        org_user, created = self.org.get_or_add_user(self.user)
        self.org_user = org_user

    def test_create_nats_app(self):
        assert self.org.name == self.org.json.get("name")
        app = create_nats_app(self.user, self.org)
        assert app.organization == self.org

    def test_nsc_generate_creds(self):
        app_creds = nsc_generate_creds(self.org, self.app)
        user_creds = nsc_generate_creds(self.org, self.org_user)

        assert app_creds != user_creds

        assert ("-----BEGIN NATS USER JWT-----") in app_creds
        assert ("------END NATS USER JWT------") in app_creds
        assert ("-----BEGIN USER NKEY SEED-----") in app_creds
        assert ("------END USER NKEY SEED------") in app_creds

        assert ("-----BEGIN NATS USER JWT-----") in user_creds
        assert ("------END NATS USER JWT------") in user_creds
        assert ("-----BEGIN USER NKEY SEED-----") in user_creds
        assert ("------END USER NKEY SEED------") in user_creds
