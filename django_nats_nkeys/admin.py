from django.contrib import admin

# from .models import (
#     TurnAdmin,
#     TurnUser,
#     AllowedPeerIp,
#     DeniedPeerIp,
#     OauthKey,
#     TurnOriginToRealm,
#     TurnRealmOption,
#     TurnSecret,
# )


# @admin.register(TurnAdmin)
# class TurnAdminView(admin.ModelAdmin):
#     list_display = ("name", "realm", "django_user_id")


# @admin.register(TurnUser)
# class TurnUserAdmin(admin.ModelAdmin):
#     list_display = ("name", "realm", "django_user_id")


# @admin.register(AllowedPeerIp)
# class AllowedPeerIpAdmin(admin.ModelAdmin):
#     list_display = ("realm", "ip_range")


# @admin.register(DeniedPeerIp)
# class DeniedPeerIpAdmin(admin.ModelAdmin):
#     list_display = ("realm", "ip_range")


# @admin.register(OauthKey)
# class OauthKeyAdmin(admin.ModelAdmin):
#     list_display = ("kid", "ikm_key", "timestamp", "lifetime", "as_rs_alg", "realm")


# @admin.register(TurnOriginToRealm)
# class TurnOriginToRealm(admin.ModelAdmin):
#     list_display = ("origin", "realm")


# @admin.register(TurnRealmOption)
# class TurnRealmOption(admin.ModelAdmin):
#     list_display = ("opt", "realm", "value")


# @admin.register(TurnSecret)
# class TurnRealmOption(admin.ModelAdmin):
#     list_display = (
#         "realm",
#         "value",
#     )
