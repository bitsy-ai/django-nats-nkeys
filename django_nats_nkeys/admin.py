from django.contrib import admin

from django_nats_nkeys.settings import nats_nkeys_settings

from organizations.models import (
    Organization,
    OrganizationUser,
    OrganizationOwner,
    OrganizationInvitation,
)

NatsOrganization = nats_nkeys_settings.get_nats_account_model()
NatsOrganizationOwner = nats_nkeys_settings.get_nats_account_owner_model()
NatsApp = nats_nkeys_settings.get_nats_app_model()
NatsOrganizationUser = nats_nkeys_settings.get_nats_user_model()


@admin.register(NatsOrganization)
class NatsOrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsApp)
class NatsOrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsOrganizationOwner)
class NatsOrganizationOwnerAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsOrganizationUser)
class NatsAccountOwnerAdmin(admin.ModelAdmin):
    pass


# unregister django organization defaults and register our own
admin.site.unregister(Organization)
admin.site.unregister(OrganizationUser)
admin.site.unregister(OrganizationOwner)
admin.site.unregister(OrganizationInvitation)
