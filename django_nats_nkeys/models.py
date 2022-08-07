from django.db import models
from organizations.abstract import (
    AbstractOrganization,
    AbstractOrganizationUser,
    AbstractOrganizationOwner,
    AbstractOrganizationInvitation,
)
from coolname import generate_slug


# ref: https://django-organizations.readthedocs.io/en/latest/cookbook.html#multiple-organizations-with-simple-inheritance


def _default_name():
    return generate_slug(3)


class NatsOrganization(AbstractOrganization):
    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )


class NatsOrganizationUser(AbstractOrganizationUser):
    """
    Corresponds to a NATS user/client, intended for use for a human who owns one or more NatsApp instances and wants to publish/subscribe to all apps via signed credential.
    """

    app_name = models.CharField(max_length=255, default=_default_name)
    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )


class AbstractNatsApp(models.Model):
    """
    Corresponds to a NATS user/client within an Account group, intended for use by application
    https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["app_name", "organization_user"],
                name="unique_app_name_per_org_user",
            )
        ]

    app_name = models.CharField(max_length=255, default=_default_name)
    organization_user = models.ForeignKey(
        NatsOrganizationUser, on_delete=models.CASCADE, related_name="nats_apps"
    )
    organization = models.ForeignKey(
        NatsOrganization,
        on_delete=models.CASCADE,
        related_name="nats_apps",
    )
    json = models.JSONField(
        max_length=255,
        help_text="Output of `nsc describe account`",
    )


class NatsApp(AbstractNatsApp):
    """
    Corresponds to a NATS user/client within an Account group
    https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """

    pass


class NatsOrganizationOwner(AbstractOrganizationOwner):
    """Identifies ONE user, by AccountUser, to be the owner"""

    pass


class NatsAccountInvitation(AbstractOrganizationInvitation):
    """Stores invitations for adding users to organizations"""

    pass
