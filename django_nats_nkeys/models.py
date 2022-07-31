# References: https://github.com/coturn/coturn/blob/master/turndb/schema.sql

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


class NatsApp(models.Model):
    """
    Corresponds to a NATS user/client within an Account group
    https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "org_user"], name="unique_app_name_per_org_user"
            )
        ]

    name = models.CharField(max_length=255)
    org_user = models.ForeignKey(NatsOrganizationUser, on_delete=models.CASCADE)
    org = models.ForeignKey(NatsOrganization, on_delete=models.CASCADE)
    json = models.JSONField(
        max_length=255, help_text="Output of `nsc describe account`", default=dict
    )


class NatsOrganizationOwner(AbstractOrganizationOwner):
    """Identifies ONE user, by AccountUser, to be the owner"""

    pass


class NatsAccountInvitation(AbstractOrganizationInvitation):
    """Stores invitations for adding users to organizations"""

    pass
