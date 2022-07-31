from django.db import models
from organizations.abstract import (
    AbstractOrganization,
    AbstractOrganizationUser,
    AbstractOrganizationOwner,
    AbstractOrganizationInvitation,
)

# ref: https://django-organizations.readthedocs.io/en/latest/cookbook.html#multiple-organizations-with-simple-inheritance


class NatsOrganization(AbstractOrganization):
    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )


class NatsOrganizationUser(AbstractOrganizationUser):
    pass


class AbstractNatsApp(models.Model):
    """
    Corresponds to a NATS user/client within an Account group
    https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=["name", "organization_user"],
                name="unique_app_name_per_org_user",
            )
        ]

    name = models.CharField(max_length=255)
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
