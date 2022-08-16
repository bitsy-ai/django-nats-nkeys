# Django Nats NKEYS

[![image](https://img.shields.io/pypi/v/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/) [![image](https://img.shields.io/pypi/pyversions/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/) [![image](https://img.shields.io/pypi/djversions/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/) [![image](https://img.shields.io/pypi/wheel/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/) [![image](https://img.shields.io/discord/773452324692688956)](https://discord.gg/Y848Hq9xKh) [![image](https://img.shields.io/github/workflow/status/bitsy-ai/django-nats-nkeys/Test)](https://github.com/bitsy-ai/django-nats-nkeys) [![image](https://img.shields.io/codecov/c/github/bitsy-ai/django-nats-nkeys)](https://github.com/bitsy-ai/django-nats-nkeys) [![image](https://img.shields.io/github/release-date-pre/bitsy-ai/django-nats-nkeys)](https://github.com/bitsy-ai/django-nats-nkeys)

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


Settings
===========

### Basic Settings
`NATS_NSC_DATA_DIR` (default: `"/var/lib/nats/nsc/stores"` or `$NSC_STORE` environment var)
`NATS_NSC_CONFIG_DIR`(default: `"/var/lib/nats/nsc/config"` or `$NSC_HOME` environment var)
`NATS_NSC_KEYSTORE_DIR` (default: `"/var/lib/nats/nsc/keys"` or `$NKEYS_PATH` environment var)
`NATS_SERVER_URI` (default: `"nats://nats:4223"`)
`NATS_NKEYS_IMPORT_DIR` (default: `".nats/"`, )
`NATS_NKEYS_EXPORT_DIR` (default: `".nats/"`)
`NATS_NKEYS_OPERATOR_NAME` (default: `"DjangoOperator"`)


### Organization Models
* Based on [Django organizations](https://github.com/bennylope/django-organizations)
* An `Organization` represents an `account` in [NATS multi-tenant account model](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts)
* An `App` represents a `user` in [NATS multi-tenant account model](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts)
  

`NATS_ORGANIZATION_MODEL` (default: `"django_nats_nkeys.NatsOrganization"`)
* Must subclass `django_nats_nkeys.models.NatsOrganization`

`NATS_ORGANIZATION_OWNER_MODEL` (default: `"django_nats_nkeys.NatsOrganizationOwner"`)
* Must subclass `django_nats_nkey.models.NatsOrganizationOwner`

`NATS_ORGANIZATION_APP_MODEL` (default: `"django_nats_nkey.NatsOrganizationApp"`)
* Must subclass `django_nats_nkey.models.AbstractNatsApp`

`NATS_ORGANIZATION_USER_MODEL` (default: `"django_nats_nkeys.models.NatsOrganizationUser"`)
* Must subclass `django_nats_nkeys.models.NatsOrganizationUser`


### Robot/Automation Models

`NATS_ROBOT_APP_MODEL` (default: `"django_nats_nkeys.NatsRobotApp"`)
`NATS_ROBOT_ACCOUNT_MODEL` (default: `"django_nats_nkeys.NatsRobotAccount"`)

