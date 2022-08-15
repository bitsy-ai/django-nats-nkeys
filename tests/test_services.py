from wsgiref.validate import validator
from django.test import TestCase
from django.contrib.auth import get_user_model

from django_nats_nkeys.services import (
    NatsOrganizationUser,
    nsc_describe_json,
    nsc_validate,
)
from django_nats_nkeys.models import (
    NatsMessageExport,
    NatsMessageExportType,
    NatsOrganizationApp,
    NatsOrganizationOwner,
    NatsRobotAccount,
    NatsRobotApp,
)
from coolname import generate_slug

from django_nats_nkeys.services import (
    create_organization,
    nsc_describe_json,
    nsc_generate_creds,
)

User = get_user_model()


class TestServices(TestCase):
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

    def test_create_org_app(self):
        org_user = self.org_user
        app = self.app
        assert app.organization == self.org
        assert app.organization_user == org_user

        # assert app json matches nsc describe output
        assert app.json == nsc_describe_json(
            app.organization.name, app_name=app.app_name
        )

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

    def test_create_robot_app(self):
        assert self.robot_app.app_name == self.robot_app_name
        assert self.robot_app.json == nsc_describe_json(
            self.robot_app.account.name, app_name=self.robot_app.app_name
        )

    def test_imports_and_exports_stream(self):
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

    def test_validator(self):
        validator = nsc_validate(account_name=self.org_name)
        assert validator.ok() is True
        validator = nsc_validate(account_name=self.robot_account.name)
        assert validator.ok() is True
