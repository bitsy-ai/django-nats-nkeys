from unittest.mock import patch
from django.test import TestCase, override_settings
from datetime import datetime, timezone, tzinfo
from freezegun import freeze_time

# class TestServices(TestCase):
#     @override_settings(COTURN_CREDENTIAL_MAX_AGE=3600)
#     def test_get_expiration_timestamp_default(self):
#         expected = int(datetime(2021, 9, 14, 1, tzinfo=timezone.utc).timestamp())
#         with freeze_time("2021-09-14 00:00:00", tz_offset=0):
#             actual = _get_expiration_timestamp()
#         assert expected == actual

#     # def test_create_turn_api_credentials(self):
#     #     mock_datetime_now = datetime
#     #     email = "test-user@test.com"
#     #     username, password = create_turn_api_credentials(email)
