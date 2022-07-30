from django.test import TestCase
from django.contrib.auth import get_user_model
from django_nats_nkeys.services import create_nats_account_org, create_nats_app
from coolname import generate_slug

User = get_user_model()


class TestServices(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = User.objects.create(
            email="admin@test.com", password="testing1234", is_superuser=False
        )

    def test_create_nats_app(self):
        org = create_nats_account_org(self.user)
        assert org.name == org.json.get("name")

        app = create_nats_app(self.user, org)

        assert app.org == org
