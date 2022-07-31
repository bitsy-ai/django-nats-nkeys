# Django Nats NKEYS

[![image](https://img.shields.io/pypi/v/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/)

[![image](https://img.shields.io/pypi/pyversions/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/)

[![image](https://img.shields.io/pypi/djversions/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/)

[![image](https://img.shields.io/pypi/wheel/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/)

[![image](https://img.shields.io/discord/773452324692688956)](https://discord.gg/Y848Hq9xKh)

[![image](https://img.shields.io/github/workflow/status/bitsy-ai/django-nats-nkeys/Test)](https://github.com/bitsy-ai/django-nats-nkeys)

[![image](https://img.shields.io/codecov/c/github/bitsy-ai/django-nats-nkeys)](https://github.com/bitsy-ai/django-nats-nkeys)

[![image](https://img.shields.io/github/release-date-pre/bitsy-ai/django-nats-nkeys)](https://github.com/bitsy-ai/django-nats-nkeys)

[NATS](https://docs.nats.io/nats-concepts/what-is-nats) is an
infrastructure platform for building message-based services.

This Django app integrates [NAT's multi-tenant account paradigm](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts) with [Django Organizations](https://github.com/bennylope/django-organizations).

The NATS `nsc` tool is used to manage operator, account, and user JWTs.


Quick start
===========

1.  Add to your INSTALLED\_APPS settings:

        INSTALLED_APPS = [
            ...
            "organizations",
            "django_extensions",
            "django_nats_nkey",
        ]

2.  Run `python manage.py migrate` to create the NATS organizationals
    models

3.  Run `python manage.py nsc-init` (optional) Initialize a new NATS
    operator. You are responsible for copying the generated
    `.conf` file to your NATS server. If you choose to use
    an existing operator, you are responsible for running `nsc pull` as a pre-deployment step.

Contributor's Guide
====================

1.  Create a development environment (requires docker & docker-compose):

        make docker-up
        make nsc-init

2.  Run tests and generate a coverage report:

        make pytest

3.  Run `black` linter:

        make lint
