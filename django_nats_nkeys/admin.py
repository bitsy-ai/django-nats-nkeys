from django.contrib import admin

from django_nats_nkeys.settings import nats_nkeys_settings
from django_nats_nkeys.models import NatsMessageExport, NatsRobotAccount

from organizations.models import (
    Organization,
    OrganizationUser,
    OrganizationOwner,
    OrganizationInvitation,
)

NatsOrganization = nats_nkeys_settings.get_nats_account_model()
NatsOrganizationOwner = nats_nkeys_settings.get_nats_organization_owner_model()
NatsOrganizationUser = nats_nkeys_settings.get_nats_user_model()
NatsAppModels = nats_nkeys_settings.get_nats_app_models()
NatsRobotAccount = nats_nkeys_settings.get_nats_robot_account_model()


@admin.register(NatsMessageExport)
class NatsNatsMessageExportAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsOrganization)
class NatsOrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsOrganizationOwner)
class NatsOrganizationOwnerAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsOrganizationUser)
class NatsOrganizationUserAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsRobotAccount)
class NatsRobotAccountAdmin(admin.ModelAdmin):
    pass


for model in NatsAppModels:

    @admin.register(model)
    class NatsAppModelAdmin(admin.ModelAdmin):
        pass
