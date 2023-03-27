from .test import *
import os
import sys
from pathlib import Path


DATABASES = {
    "default": {
        "USER": "debug",
        "ENGINE": "django.db.backends.postgresql",
        "PASSWORD": "debug",
        "HOST": "localhost",
        "PORT": 5432,
        "NAME": "django",
    }
}

NATS_SERVER_URI = "nats://localhost:4223"
