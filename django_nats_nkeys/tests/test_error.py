from unittest.mock import patch
import pytest
from django.test import TestCase, override_settings
from django_nats_nkeys.errors import NscConflict

from django_nats_nkeys.services import (
    nsc_add_account,
    nsc_describe_json,
    nsc_validate,
    nsc_add_app,
    create_organization,
)
from django.contrib.auth import get_user_model

from coolname import generate_slug
from django_nats_nkeys.models import (
    NatsMessageExport,
    NatsMessageExportType,
    NatsOrganizationApp,
    NatsOrganizationOwner,
    NatsRobotAccount,
    NatsRobotApp,
    NatsOrganizationUser,
)

User = get_user_model()


class TestErrors(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(
            email="admin@test.com", password="testing1234", is_superuser=False
        )
        cls.org_name = generate_slug(3)
        cls.org = create_organization(
            cls.user,
            cls.org_name,
            org_user_defaults={"is_admin": True},
        )

        cls.org_user = NatsOrganizationUser.objects.get(user=cls.user)
        cls.org_owner = NatsOrganizationOwner.objects.get(organization=cls.org)

        cls.app_name = generate_slug(3)

        cls.app = NatsOrganizationApp.objects.create_nsc(
            app_name=cls.app_name,
            organization_user=cls.org_user,
            organization=cls.org_user.organization,
        )
        cls.robot_name = generate_slug(3)
        cls.robot_account = NatsRobotAccount.objects.create_nsc(name=cls.robot_name)
        cls.robot_app_name = generate_slug(3)

    @override_settings(NATS_NSC_RETRY_MODE="IDEMPOTENT")
    def test_nsc_account_conflict_warn(self):
        # nsc_add_account should log warning if account already exists
        with patch("django_nats_nkeys.services.logger") as mock_logger:
            nsc_add_account(self.org)
            assert mock_logger.warning.called

    @override_settings(NATS_NSC_RETRY_MODE="STRICT")
    def test_nsc_account_conflict_error(self):
        # nsc_add_account should log warning if account already exists
        with pytest.raises(NscConflict) as e:
            nsc_add_account(self.org)

    @override_settings(NATS_NSC_RETRY_MODE="IDEMPOTENT")
    def test_nsc_app_conflict_warn(self):
        # nsc_add_account should log warning if account already exists
        with patch("django_nats_nkeys.services.logger") as mock_logger:
            nsc_add_app(self.org.name, self.app_name, self.app)
            assert mock_logger.warning.called

    @override_settings(NATS_NSC_RETRY_MODE="STRICT")
    def test_nsc_app_conflict_error(self):
        # nsc_add_account should log warning if account already exists
        with pytest.raises(NscConflict) as e:
            nsc_add_app(self.org.name, self.app_name, self.app)
