from typing import Any

from django.contrib import admin

from django_nats_nkeys.settings import nats_nkeys_settings
from django_nats_nkeys.models import NatsMessageExport, NatsRobotAccount
from django.db.models import QuerySet
from django.http import HttpRequest

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
NatsOrganizationApp = nats_nkeys_settings.get_nats_organization_app_model()
NatsRobotAppModel = nats_nkeys_settings.get_nats_robot_app_model()


@admin.register(NatsMessageExport)
class NatsNatsMessageExportAdmin(admin.ModelAdmin):
    pass


def enable_jetstream(
    _modeladmin,
    request: HttpRequest,
    queryset: QuerySet[Any],
):

    for org in queryset:
        org.jetstream_enabled = True
        # update_fields is required to trigger nsc account edit in signals.py
        org.save(update_fields=["jetstream_enabled"])


@admin.register(NatsOrganization)
class NatsOrganizationAdmin(admin.ModelAdmin):
    actions = [
        enable_jetstream,
    ]

    def get_imports(self, obj):
        return [s.name for s in obj.imports.all()]

    def get_exports(self, obj):
        return [s.name for s in obj.exports.all()]

    list_display = ("name", "get_imports", "get_exports", "jetstream_enabled", "json")


@admin.register(NatsOrganizationOwner)
class NatsOrganizationOwnerAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsOrganizationUser)
class NatsOrganizationUserAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsRobotAccount)
class NatsRobotAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(NatsRobotAppModel)
class NatsRobotAppAdmin(admin.ModelAdmin):
    pass


def enable_bearer_auth(
    _modeladmin,
    request: HttpRequest,
    queryset: QuerySet[Any],
):

    for app in queryset:
        app.bearer = True
        # update_fields is required to trigger nsc user edit in signals.py
        app.save(update_fields=["bearer"])


@admin.register(NatsOrganizationApp)
class NatsOrganizationAppAdmin(admin.ModelAdmin):
    actions = ["enable_bearer_auth"]
