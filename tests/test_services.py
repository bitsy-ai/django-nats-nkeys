import pytest
import tempfile
import zipfile
import os
from asgiref.sync import async_to_sync, sync_to_async

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django_nats_nkeys.models import (
    NatsMessageExport,
    NatsMessageExportType,
    NatsOrganizationApp,
    NatsOrganizationOwner,
    NatsRobotAccount,
    NatsRobotApp,
    NatsOrganizationUser,
)
from coolname import generate_slug
import nats
import paho.mqtt.client as mqtt

from django_nats_nkeys.services import (
    create_organization,
    nsc_describe_json,
    nsc_generate_creds,
    nsc_validate,
)

User = get_user_model()

TEST_NATS_URI = "nats://nats:4223"
TEST_MQTT_PORT = 1883


class TestBearerAuthentication(TestCase):
    """
    Tests for AbstractNatsApp.bearer authentication
    """

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
            org_defaults={"jetstream_enabled": True},
        )
        cls.org_user = NatsOrganizationUser.objects.get(user=cls.user)
        cls.org_owner = NatsOrganizationOwner.objects.get(organization=cls.org)

        cls.app_name = generate_slug(3)

        cls.app = NatsOrganizationApp.objects.create_nsc(
            app_name=cls.app_name,
            organization_user=cls.org_user,
            organization=cls.org_user.organization,
        )

    async def test_generate_creds_zip(self):
        filename, zipfiledata = self.app.generate_creds_zip()
        with tempfile.NamedTemporaryFile() as f:
            f.write(zipfiledata)
            with tempfile.TemporaryDirectory() as d:
                with zipfile.ZipFile(f, "r") as z:
                    z.extractall(d)

                # test nats connection
                nc = await nats.connect(
                    TEST_NATS_URI, user_credentials=os.path.join(d, filename)
                )

    def test_generate_creds_idempotent(self):
        # unless a JWT component changes, generate creds should be idempotent
        creds1 = self.app.generate_creds()
        creds2 = self.app.generate_creds()
        creds3 = self.app.generate_creds()
        assert creds1 == creds2 == creds3

    def test_bearer_token_enable_existing(self):
        """
        Test enabling bearer authentication for existing app
        """
        # NATS clients are required to sign a nonce sent by the server using their private key
        # this is the default authentication behavior

        # test nonce_app can connect to NATS server
        creds = self.app.generate_creds()
        jwt = self.app.generate_jwt()

        # MQTT clients can't receive and then send back a signed nonce, but we can enable using the JWT as a bearer token
        self.app.bearer = True
        self.app.save(update_fields=["bearer"])
        self.app.refresh_from_db()

        assert self.app.json.get("nats", {}).get("bearer_token") == True
        creds2 = self.app.generate_creds()
        jwt2 = self.app.generate_jwt()

        # flipping the bearer authentication bit will generate a different JWT, since NATS JWTs incorporate capabilities of entity
        assert creds != creds2
        assert jwt2 != jwt

        # import pdb

        # pdb.set_trace()

        mqttc = mqtt.Client(self.app_name, clean_session=True)
        mqttc.username_pw_set("anyusernameisvalid", jwt2)
        mqttc.connect("nats", TEST_MQTT_PORT)
        mqttc.loop_start()

        msg = mqttc.publish("testing/temperature", payload=b"90")
        assert msg.rc == 0

    def test_bearer_token_enable_new(self):
        """
        Test enabling bearer authentication for new app
        """
        app_name = generate_slug(3)
        app = NatsOrganizationApp.objects.create_nsc(
            app_name=app_name,
            organization_user=self.org_user,
            organization=self.org_user.organization,
            bearer=True,
        )

        jwt = self.app.generate_jwt()

        # verify jwt can be used as a bearer token to establish mqtt connection
        mqttc = mqtt.Client(app_name, clean_session=True)
        mqttc.username_pw_set("anyusernameisvalid", jwt)
        mqttc.connect("nats", TEST_MQTT_PORT, keepalive=1)
        mqttc.loop_start()

        msg = mqttc.publish("testing/temperature", payload=b"90")
        assert msg.rc == 0


class TestSharedServices(TestCase):
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
        cls.robot_app = NatsRobotApp.objects.create_nsc(
            app_name=cls.robot_app_name, account=cls.robot_account
        )

    def test_create_organization(self):
        org = self.org
        # assert organization was created and json matches nsc describe output
        assert org.name == self.org_name
        org_json = nsc_describe_json(org.name)
        assert org.json == org_json

        # assert organization owner was created and is user
        org_user = self.org_user
        org_owner = self.org_owner

        assert org.owner == org_owner
        assert org_owner.organization_user == org_user

        # assert user json matches nsc describe output
        user_json = nsc_describe_json(
            org_user.organization.name, app_name=org_user.app_name
        )
        assert org_user.json == user_json

        # assert nsc validation is ok
        assert org.nsc_validate().ok() is True
        assert org_user.nsc_validate().ok() is True

    def test_enable_jetstream_organization(self):
        before_describe_json = nsc_describe_json(self.org.name)
        self.org.jetstream_enabled = True
        self.org.save(update_fields=["jetstream_enabled"])

        after_describe_json = nsc_describe_json(self.org.name)
        assert self.org.json == after_describe_json
        assert self.org.json != before_describe_json
        assert (
            self.org.json.get("nats", {}).get("limits", {}).get("consumer")
            == self.org.jetstream_max_consumers
        )
        assert (
            self.org.json.get("nats", {}).get("limits", {}).get("streams")
            == self.org.jetstream_max_streams
        )

    def test_create_org_app(self):
        org_user = self.org_user
        app = self.app
        assert app.organization == self.org
        assert app.organization_user == org_user

        # assert app json matches nsc describe output
        assert app.json == nsc_describe_json(
            app.organization.name, app_name=app.app_name
        )

        # assert nsc validation is ok
        assert app.nsc_validate().ok() is True

    def test_nsc_generate_creds(self):
        app_creds = nsc_generate_creds(self.app.organization.name, self.app.app_name)
        user_creds = nsc_generate_creds(
            self.org_user.organization.name, self.org_user.app_name
        )
        robot_app_creds = nsc_generate_creds(
            self.robot_app.account.name, self.robot_app.app_name
        )

        assert app_creds != user_creds != robot_app_creds

        assert ("-----BEGIN NATS USER JWT-----") in app_creds
        assert ("------END NATS USER JWT------") in app_creds
        assert ("-----BEGIN USER NKEY SEED-----") in app_creds
        assert ("------END USER NKEY SEED------") in app_creds

        assert ("-----BEGIN NATS USER JWT-----") in user_creds
        assert ("------END NATS USER JWT------") in user_creds
        assert ("-----BEGIN USER NKEY SEED-----") in user_creds
        assert ("------END USER NKEY SEED------") in user_creds

        assert ("-----BEGIN NATS USER JWT-----") in robot_app_creds
        assert ("------END NATS USER JWT------") in robot_app_creds
        assert ("-----BEGIN USER NKEY SEED-----") in robot_app_creds
        assert ("------END USER NKEY SEED------") in robot_app_creds

    def test_create_robot_account(self):
        assert self.robot_account.name == self.robot_name
        # assert robot account json matches nsc describe output
        assert self.robot_account.json == nsc_describe_json(self.robot_account.name)

        # assert nsc validation is ok
        assert self.robot_account.nsc_validate().ok() is True

    def test_create_robot_app(self):
        assert self.robot_app.app_name == self.robot_app_name
        assert self.robot_app.json == nsc_describe_json(
            self.robot_app.account.name, app_name=self.robot_app.app_name
        )

        assert self.robot_app.nsc_validate().ok() is True

    def test_validator(self):
        validator = nsc_validate(account_name=self.org_name)
        assert validator.ok() is True
        validator = nsc_validate(account_name=self.robot_account.name)
        assert validator.ok() is True

    def test_unique_robot_account(self):
        # unique account name required
        with pytest.raises(IntegrityError):
            NatsRobotAccount.objects.create_nsc(name=self.robot_name)
        # unique-per-account app name required

    def test_unique_robot_app(self):
        with pytest.raises(IntegrityError):
            NatsRobotApp.objects.create_nsc(
                app_name=self.robot_app_name, account=self.robot_account
            )


class TestIdempotentAdd(TestCase):
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
        cls.robot_app = NatsRobotApp.objects.create_nsc(
            app_name=cls.robot_app_name, account=cls.robot_account
        )

    def test_idempotent_add(self):
        # adding a relationship that already exists should be a no-op
        public_export_name = "all-public"
        public_subject_pattern = "public.>"
        public_msg_stream = NatsMessageExport.objects.create(
            name=public_export_name,
            subject_pattern=public_subject_pattern,
            public=True,
            export_type=NatsMessageExportType.STREAM,
        )

        private_export_name = "private"
        private_subject_pattern = "private.>"
        private_msg_stream = NatsMessageExport.objects.create(
            name=private_export_name,
            subject_pattern=private_subject_pattern,
            public=False,
            export_type=NatsMessageExportType.STREAM,
        )

        # add another org account importer
        partner_user = User.objects.create(
            email="private-partner@test.com",
            password="testing1234",
            is_superuser=False,
            username="private-partner",
        )
        partner_org_name = generate_slug(3)
        partner_org = create_organization(
            partner_user,
            partner_org_name,
            org_user_defaults={"is_admin": True},
        )

        partner_org.imports.add(public_msg_stream)
        partner_org.imports.add(private_msg_stream)

        expected_partner_json = partner_org.json.copy()

        self.robot_account.imports.add(public_msg_stream)
        self.robot_account.imports.add(private_msg_stream)

        expected_robot_json = self.robot_account.json.copy()

        # should not raise any exceptions / should be a no-op
        partner_org.imports.add(private_msg_stream)
        self.robot_account.imports.add(private_msg_stream)
        self.robot_account.imports.add(public_msg_stream)

        assert expected_partner_json == partner_org.json
        assert expected_robot_json == self.robot_account.json

        self.org.exports.add(private_msg_stream)
        self.org.exports.add(public_msg_stream)

        expected_org_json = self.org.json.copy()

        # should raise any exceptions / should be a no-op
        self.org.exports.add(private_msg_stream)
        assert expected_org_json == self.org.json


class TestPublicStreamExport(TestCase):
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
        cls.robot_app = NatsRobotApp.objects.create_nsc(
            app_name=cls.robot_app_name, account=cls.robot_account
        )

    def test_imports_and_exports_public_stream(self):
        export_name = "all-public"
        subject_pattern = "public.>"
        public_msg_stream = NatsMessageExport.objects.create(
            name=export_name,
            subject_pattern=subject_pattern,
            public=True,
            export_type=NatsMessageExportType.STREAM,
        )

        # pre-configure importers for stream

        # add a robot importer
        self.robot_account.imports.add(public_msg_stream)
        # add another org account importer
        partner_user = User.objects.create(
            email="partner@test.com",
            password="testing1234",
            is_superuser=False,
            username="partner",
        )
        partner_org_name = generate_slug(3)
        partner_org = create_organization(
            partner_user,
            partner_org_name,
            org_user_defaults={"is_admin": True},
        )
        partner_org.imports.add(public_msg_stream)

        # add export to NatsOrganization
        self.org.exports.add(public_msg_stream)
        assert self.org.exports.count() == 1
        # nsc describe output should contain stream
        assert self.org.json["nats"]["exports"][0] == {
            "name": export_name,
            "subject": subject_pattern,
            "type": "stream",
        }

        # imports account id matches
        partner_org.refresh_from_db()
        self.robot_account.refresh_from_db()
        self.org.refresh_from_db()

        assert partner_org.json["nats"]["imports"][0]["account"] == self.org.json["sub"]
        assert (
            self.robot_account.json["nats"]["imports"][0]["account"]
            == self.org.json["sub"]
        )

        # subjects match
        # TODO: this will break for remote subject remapping
        assert (
            partner_org.json["nats"]["imports"][0]["subject"]
            == subject_pattern
            == self.org.json["nats"]["exports"][0]["subject"]
        )

        assert (
            self.robot_account.json["nats"]["imports"][0]["subject"]
            == subject_pattern
            == self.org.json["nats"]["exports"][0]["subject"]
        )


class TestPrivateStreamExport(TestCase):
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
        cls.robot_app = NatsRobotApp.objects.create_nsc(
            app_name=cls.robot_app_name, account=cls.robot_account
        )

    def test_imports_and_exports_private_stream(self):
        export_name = "private"
        subject_pattern = "private.>"
        private_msg_stream = NatsMessageExport.objects.create(
            name=export_name,
            subject_pattern=subject_pattern,
            public=False,
            export_type=NatsMessageExportType.STREAM,
        )

        # add a robot importer
        self.robot_account.imports.add(private_msg_stream)

        # add another org account importer
        partner_user = User.objects.create(
            email="private-partner@test.com",
            password="testing1234",
            is_superuser=False,
            username="private-partner",
        )
        partner_org_name = generate_slug(3)
        partner_org = create_organization(
            partner_user,
            partner_org_name,
            org_user_defaults={"is_admin": True},
        )
        partner_org.imports.add(private_msg_stream)

        # add export to NatsOrganization
        self.org.exports.add(private_msg_stream)
        assert self.org.exports.count() == 1
        # nsc describe output should contain stream
        assert self.org.json["nats"]["exports"][0] == {
            "name": export_name,
            "subject": subject_pattern,
            "type": "stream",
            "token_req": True,
        }

        # imports account id matches
        partner_org.refresh_from_db()
        self.robot_account.refresh_from_db()
        self.org.refresh_from_db()

        assert partner_org.json["nats"]["imports"][0]["account"] == self.org.json["sub"]
        assert (
            self.robot_account.json["nats"]["imports"][0]["account"]
            == self.org.json["sub"]
        )

        # subjects match
        # TODO: this will break for remote subject remapping
        assert (
            partner_org.json["nats"]["imports"][0]["subject"]
            == subject_pattern
            == self.org.json["nats"]["exports"][0]["subject"]
        )

        assert (
            self.robot_account.json["nats"]["imports"][0]["subject"]
            == subject_pattern
            == self.org.json["nats"]["exports"][0]["subject"]
        )
