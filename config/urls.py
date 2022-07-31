from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("coturn/", include("django_coturn.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]
