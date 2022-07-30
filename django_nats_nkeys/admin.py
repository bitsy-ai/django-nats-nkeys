from django.contrib import admin

from .models import NatsOrganization, NatsAccountOwner, NatsApp, NatsOrganizationUser
from organizations.models import (
    Organization,
    OrganizationUser,
    OrganizationOwner,
    OrganizationInvitation,
)


@admin.register(NatsOrganization)
class NatsOrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsApp)
class NatsOrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsAccountOwner)
class NatsAccountOwnerAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsOrganizationUser)
class NatsAccountOwnerAdmin(admin.ModelAdmin):
    pass


# unregister django organization defaults and register our own
admin.site.unregister(Organization)
admin.site.unregister(OrganizationUser)
admin.site.unregister(OrganizationOwner)
admin.site.unregister(OrganizationInvitation)
