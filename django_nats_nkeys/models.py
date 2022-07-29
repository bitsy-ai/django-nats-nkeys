# References: https://github.com/coturn/coturn/blob/master/turndb/schema.sql

from django.db import models
from organizations.abstract import AbstractOrganization, AbstractOrganizationUser, AbstractOrganizationOwner, AbstractOrganizationInvitation

# ref: https://django-organizations.readthedocs.io/en/latest/cookbook.html#multiple-organizations-with-simple-inheritance

class NatsAccount(AbstractOrganization):
    """
        Corresponds to a single NATS Account, which allows a grouping of clients
        https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """
    pass

class NatsUser(AbstractOrganizationUser):
    """
        Corresponds to a NATS user/client within an Account group
        https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts
    """
    nkey = models.CharField(max_length=255)

class NatsAccountOwner(AbstractOrganizationOwner):
    """Identifies ONE user, by AccountUser, to be the owner"""
    pass

class NatsAccountInvitation(AbstractOrganizationInvitation):
    """Stores invitations for adding users to organizations"""
    pass
