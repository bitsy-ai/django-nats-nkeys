"""
dj-stripe Migrations Tests
"""
import pytest
from django.test import TestCase, override_settings
from django.core.exceptions import ImproperlyConfigured
from django_nats_nkeys.settings import nats_nkeys_settings


class TestSettings(TestCase):
    def setUp(self):
        return super().setUp()

    @override_settings(NATS_NSC_KEYSTORE_DIR="/tmp/nsc/keys")
    def test_custom_nsc_keystore(self):
        assert nats_nkeys_settings.NATS_NSC_KEYSTORE_DIR == "/tmp/nsc/keys"

    @override_settings(NATS_NSC_CONFIG_DIR="/tmp/nsc/")
    def test_custom_nsc_home(self):
        assert nats_nkeys_settings.NATS_NSC_CONFIG_DIR == "/tmp/nsc/"

    @override_settings(NATS_NSC_DATA_DIR="/tmp/nsc/store")
    def test_custom_run_nsc_and_log_output(self):
        assert nats_nkeys_settings.NATS_NSC_DATA_DIR == "/tmp/nsc/store"

    @override_settings(NATS_NKEYS_IMPORT_DIR="/etc/django-nats-operator")
    def test_custom_export_dir(self):
        assert nats_nkeys_settings.NATS_NKEYS_IMPORT_DIR == "/etc/django-nats-operator"

    @override_settings(NATS_NKEYS_EXPORT_DIR="/etc/django-nats-operator")
    def test_custom_export_dir(self):
        assert nats_nkeys_settings.NATS_NKEYS_EXPORT_DIR == "/etc/django-nats-operator"

    @override_settings(NATS_NKEYS_OPERATOR_NAME="MyCustomOperator")
    def test_custom_operator_name(self):
        assert nats_nkeys_settings.NATS_NKEYS_OPERATOR_NAME == "MyCustomOperator"

    @override_settings(NATS_ORGANIZATION_MODEL="invalid")
    def test_invalid_account_model(self):
        with pytest.raises(ImproperlyConfigured):
            nats_nkeys_settings.get_nats_account_model()

    @override_settings(NATS_ORGANIZATION_OWNER_MODEL="invalid")
    def test_invalid_account_owner_model(self):
        with pytest.raises(ImproperlyConfigured):
            nats_nkeys_settings.get_nats_organization_owner_model()

    @override_settings(NATS_ORGANIZATION_APP_MODEL="invalid")
    def test_invalid_app_model(self):
        with pytest.raises(ImproperlyConfigured):
            nats_nkeys_settings.get_nats_organization_app_model()

    @override_settings(NATS_ORGANIZATION_USER_MODEL="invalid")
    def test_invalid_user_model(self):
        with pytest.raises(ImproperlyConfigured):
            nats_nkeys_settings.get_nats_user_model()

    @override_settings(NATS_ROBOT_ACCOUNT_MODEL="invalid")
    def test_invalid_robot_account_model(self):
        with pytest.raises(ImproperlyConfigured):
            nats_nkeys_settings.get_nats_robot_account_model()

    @override_settings(NATS_ROBOT_APP_MODEL="invalid")
    def test_invalid_robot_app_model(self):
        with pytest.raises(ImproperlyConfigured):
            nats_nkeys_settings.get_nats_robot_app_model()

    def test_defaults_valid(self):
        from django_nats_nkeys.models import (
            NatsOrganization,
            NatsOrganizationUser,
            NatsOrganizationOwner,
            NatsOrganizationApp,
            NatsRobotApp,
        )

        assert nats_nkeys_settings.get_nats_user_model() is NatsOrganizationUser
        assert nats_nkeys_settings.get_nats_account_model() is NatsOrganization
        assert (
            nats_nkeys_settings.get_nats_organization_owner_model()
            is NatsOrganizationOwner
        )
        assert (
            nats_nkeys_settings.get_nats_organization_app_model() is NatsOrganizationApp
        )

        assert nats_nkeys_settings.get_nats_app_models() == [
            NatsOrganizationApp,
            NatsRobotApp,
        ]
