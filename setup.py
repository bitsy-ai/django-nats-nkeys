#!/usr/bin/env python
import os
from typing import List

from setuptools import setup, find_namespace_packages
from django_nats_nkeys import __version__

long_description: str = open(
    os.path.join(os.path.dirname(__file__), "README.md")
).read()
install_requires = [
    "coolname",
    "django",
    "psycopg2",
    "django-extensions",
    "django-organizations",
    "nats-py[nkeys]",
]

extras = {"drf": ["djangorestframework"]}
python_requires = ">3.6.9"
setup(
    name="django_nats_nkeys",
    version=__version__,
    packages=find_namespace_packages(exclude=["test", "tests", "config"]),
    author="Leigh Johnson",
    author_email="leigh@bitsy.ai",
    description="Django NATS Nkey is a Django app to synchronize Django superusers, accounts, and users with NATS nkey-based authentization/authorization scheme",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GNU AGPLv3",
    keywords="django NATS",
    url="http://github.com/bitsy-ai/django-nats-nkey",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
    ],
    zip_safe=True,
    install_requires=install_requires,
    test_suite="pytest",
    python_requires=python_requires,
    include_package_data=True,
    extras_require=extras,
)
