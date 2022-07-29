import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

# from django_nats_nkeys.enum import CoturnAuthStrategy
# from django_nats_nkeys.models import TurnAdmin, TurnUser
# from django_nats_nkeys.settings import coturn_settings


ADMIN_EMAIL = "admin@test.com"
USER_EMAIL = "user@test.com"


# class TestUserTurnAdminFK(TestCase):
#     @override_settings(
#         COTURN_USER_MODEL="testapp.CustomUser",
#         COTURN_USER_MODEL_REQUEST_CALLBACK=(lambda request: request.user),
#     )
#     def setUp(self):
#         return super().setUp()

#     @override_settings(COTURN_AUTH_STRATEGY=CoturnAuthStrategy.TURN_REST_API)
#     def test_admin_user_created_for_django_superuser(self):
#         UserModel = get_user_model()
#         password = UserModel.objects.make_random_password()
#         admin_user = UserModel(
#             email=ADMIN_EMAIL, username=ADMIN_EMAIL, is_superuser=True
#         )
#         admin_user.set_password(password)
#         admin_user.save()
