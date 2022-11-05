import zipfile
import io
from dataclasses import dataclass
from typing import Tuple
from django.db import models

from organizations.abstract import (
    AbstractOrganization,
    AbstractOrganizationUser,
    AbstractOrganizationOwner,
    AbstractOrganizationInvitation,
)
from organizations.managers import OrgManager, ActiveOrgManager

from coolname import generate_slug


# ref: https://django-organizations.readthedocs.io/en/latest/cookbook.html#multiple-organizations-with-simple-inheritance


class NatsMessageExportType(models.TextChoices):
    SERVICE = (
        "service",
        "Export is a service: https://docs.nats.io/using-nats/nats-tools/nsc/services",
    )
    STREAM = (
        "stream",
        "Export is a stream: https://docs.nats.io/using-nats/nats-tools/nsc/streams",
    )


class NatsMessageExport(models.Model):

    name = models.CharField(unique=True, max_length=255)
    subject_pattern = models.CharField(unique=True, max_length=255)
    public = models.BooleanField()
    export_type = models.CharField(max_length=8, choices=NatsMessageExportType.choices)


class NatsOrganizationManager(OrgManager):
    def create_nsc(self, **kwargs):
        from django_nats_nkeys.services import nsc_add_account, nsc_jetstream_update

        # create django model
        org = self.create(**kwargs)
        # try create nsc account
        org = nsc_add_account(org)
        # should we enable jetstream?
        if org.jetstream_enabled:
            return nsc_jetstream_update(org)
        return org


class ActiveNatsOrganizationManager(NatsOrganizationManager, ActiveOrgManager):
    pass


def _default_name():
    return generate_slug(3)


class NatsOrganization(AbstractOrganization):

    objects = NatsOrganizationManager()
    active = ActiveNatsOrganizationManager()

    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )
    imports = models.ManyToManyField(
        NatsMessageExport, related_name="nats_organization_imports"
    )
    exports = models.ManyToManyField(
        NatsMessageExport, related_name="nats_organization_exports"
    )

    jetstream_enabled = models.BooleanField(
        default=False,
        help_text="Enable JetStream for all users/apps belonging to NatsOrganization account",
    )

    jetstream_max_mem = models.CharField(
        default="1M",
        max_length=32,
        help_text="JetStream memory resource limits (shared across all users/apps beloning to NatsOrganization account)",
    )

    jetstream_max_file = models.CharField(
        default="5M",
        max_length=32,
        help_text="JetStream file resource limits (shared across all users/apps beloning to NatsOrganization account)",
    )

    jetstream_max_streams = models.PositiveIntegerField(
        default=10,
        help_text="JetStream max number of streams (shared across all users/apps beloning to NatsOrganization account)",
    )

    jetstream_max_consumers = models.PositiveIntegerField(
        default=10,
        help_text="JetStream max number of consumers (shared across all users/apps beloning to NatsOrganization account)",
    )

    def nsc_validate(self):
        from .services import nsc_validate

        return nsc_validate(account_name=self.name)


class AbstractNatsApp(models.Model):
    """
    Corresponds to a NATS user/client within an Account group, intended for use by application
    https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """

    class Meta:
        abstract = True

    app_name = models.CharField(max_length=255, default=_default_name)
    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )

    bearer = models.BooleanField(default=False)

    allow_pub = models.CharField(
        max_length=255,
        null=True,
        help_text="add publish permissions, comma separated list. equivalent to `nsc add user ... --allow-pub=<permissions>`",
    )

    allow_pubsub = models.CharField(
        max_length=255,
        null=True,
        help_text="add publish/subscribe permissions, comma separated list. equivalent to `nsc add user ... --allow-pubsub=<permissions>`",
    )

    allow_sub = models.CharField(
        max_length=255,
        null=True,
        help_text="add subscribe permissions, comma separated list. equivalent to `nsc add user ... --allow-sub=<permissions>`",
    )
    deny_pub = models.CharField(
        max_length=255,
        null=True,
        help_text="deny publish permissions, comma separated list. equivalent to `nsc add user ... --deny-pub=<permissions>`",
    )

    deny_pubsub = models.CharField(
        max_length=255,
        null=True,
        help_text="deny publish/subscribe permissions, comma separated list. equivalent to `nsc add user ... --deny-pubsub=<permissions>`",
    )

    deny_sub = models.CharField(
        max_length=255,
        null=True,
        help_text="deny subscribe permissions, comma separated list. equivalent to `nsc add user ... --deny-sub=<permissions>`",
    )


class NatsOrganizationAppManager(models.Manager):
    def create_nsc(self, **kwargs):
        from django_nats_nkeys.services import nsc_add_app

        obj = self.create(**kwargs)
        return nsc_add_app(obj.organization.name, obj.app_name, obj)


class NatsOrganizationUser(AbstractOrganizationUser, AbstractNatsApp):
    """
    Corresponds to a NATS user/client, intended for use for a human who owns one or more NatsApp instances and wants to publish/subscribe to all apps via signed credential.
    """

    objects = NatsOrganizationAppManager()

    def nsc_validate(self):
        from .services import nsc_validate

        return nsc_validate(account_name=self.organization.name)


@dataclass(init=True, repr=True)
class NatsCredsZipfile:
    data: bytes
    creds_filename: str
    jwt_filename: str

    def filenames(self) -> Tuple[str]:
        return (self.creds_filename, self.jwt_filename)


class AbstractNatsOrganizationApp(AbstractNatsApp):
    """
    Corresponds to a NATS user/client within an Account group
    https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """

    objects = NatsOrganizationAppManager()

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["app_name", "organization_user"],
                name="unique_app_name_per_org_user",
            )
        ]

    organization_user = models.ForeignKey(
        NatsOrganizationUser,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s",
    )
    organization = models.ForeignKey(
        NatsOrganization,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s",
    )

    def generate_jwt(self) -> str:
        """
        Extracts base64-encoded JWT string from nkey credential
        Intended for use as bearer auth token in MQTT client
        """
        creds = self.generate_creds()
        parts = creds.split("\n")
        if len(parts) > 2:
            return creds.split("\n")[1]
        return creds

    def generate_creds(self) -> str:
        """
        Generates full credential will format:

        -----BEGIN NATS USER JWT-----
        <jwt>
        ------END NATS USER JWT------

        ************************* IMPORTANT *************************
        NKEY Seed printed below can be used to sign and prove identity.
        NKEYs are sensitive and should be treated as secrets.

        -----BEGIN USER NKEY SEED-----
        <seed>
        ------END USER NKEY SEED------

        *************************************************************

        """
        from django_nats_nkeys.services import nsc_generate_creds

        return nsc_generate_creds(self.organization.name, self.app_name)

    def generate_creds_zip(
        self, creds_filename="nats.creds", jwt_filename="nats.jwt"
    ) -> NatsCredsZipfile:
        """
        Returns a Tuple of (filename, compressed bytes)
        """
        creds = self.generate_creds()
        jwt = self.generate_jwt()
        # do not write sensitive credentials to disk
        # instead, write to memory buffer
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a") as zip_obj:
            zip_obj.writestr(creds_filename, creds)
            zip_obj.writestr(jwt_filename, jwt)
        return NatsCredsZipfile(
            data=zip_buffer.getvalue(),
            creds_filename=creds_filename,
            jwt_filename=jwt_filename,
        )

    def nsc_validate(self):
        from .services import nsc_validate

        return nsc_validate(account_name=self.organization.name)


class NatsOrganizationApp(AbstractNatsOrganizationApp):
    pass


class NatsOrganizationOwner(AbstractOrganizationOwner):
    """Identifies ONE user, by AccountUser, to be the owner"""

    pass


class NatsAccountInvitation(AbstractOrganizationInvitation):
    """Stores invitations for adding users to organizations"""

    pass


class NatsRobotAccountManager(models.Manager):
    def create_nsc(self, **kwargs):
        from django_nats_nkeys.services import nsc_add_account

        # create django model
        obj = self.create(**kwargs)
        # try create nsc account
        # import pdb

        # pdb.set_trace()
        return nsc_add_account(obj)


class AbstractNatsRobotAccount(models.Model):

    objects = NatsRobotAccountManager()

    class Meta:
        abstract = True

    name = models.CharField(unique=True, max_length=255)
    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )
    imports = models.ManyToManyField(
        NatsMessageExport, related_name="nats_robot_imports"
    )
    exports = models.ManyToManyField(
        NatsMessageExport, related_name="nats_robot_exports"
    )

    def nsc_validate(self):
        from .services import nsc_validate

        return nsc_validate(account_name=self.name)


class NatsRobotAccount(AbstractNatsRobotAccount):
    pass


class NatsRobotAppManager(models.Manager):
    def create_nsc(self, **kwargs):
        from django_nats_nkeys.services import nsc_add_app

        obj = self.create(**kwargs)
        return nsc_add_app(obj.account.name, obj.app_name, obj)


class NatsRobotApp(AbstractNatsApp):
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["app_name", "account"],
                name="unique_app_name_per_robot_account",
            )
        ]

    objects = NatsRobotAppManager()
    account = models.ForeignKey(
        NatsRobotAccount,
        related_name="robot_apps",
        on_delete=models.CASCADE,
    )

    def nsc_validate(self):
        from .services import nsc_validate

        return nsc_validate(account_name=self.account.name)
