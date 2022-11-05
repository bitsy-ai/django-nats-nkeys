# Django Nats NKEYS

[![image](https://img.shields.io/pypi/v/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/) [![image](https://img.shields.io/pypi/pyversions/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/) [![image](https://img.shields.io/pypi/djversions/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/) [![image](https://img.shields.io/pypi/wheel/django-nats-nkeys)](https://pypi.org/project/django-nats-nkeys/) [![image](https://img.shields.io/discord/773452324692688956)](https://discord.gg/Y848Hq9xKh) [![image](https://img.shields.io/github/workflow/status/bitsy-ai/django-nats-nkeys/Test)](https://github.com/bitsy-ai/django-nats-nkeys) [![image](https://img.shields.io/codecov/c/github/bitsy-ai/django-nats-nkeys)](https://github.com/bitsy-ai/django-nats-nkeys) [![image](https://img.shields.io/github/release-date-pre/bitsy-ai/django-nats-nkeys)](https://github.com/bitsy-ai/django-nats-nkeys)

[NATS](https://docs.nats.io/nats-concepts/what-is-nats) is an
infrastructure platform for building message-based services.

This Django app integrates [NAT's multi-tenant account paradigm](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/accounts) with [Django Organizations](https://github.com/bennylope/django-organizations).

The NATS `nsc` tool is used to manage operator, account, and user JWTs.


Quick start
===========


1. `pip install django-nats-nkeys[drf]` 

2.  Add to your INSTALLED\_APPS settings:

        INSTALLED_APPS = [
            ...
            "organizations",
            "django_extensions",
            "django_nats_nkey",
        ]

3.  Run `python manage.py migrate` to create the NATS organizationals
    models

4.  Run `python manage.py nsc-init` (optional) Initialize a new NATS
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
`NATS_SERVER_URI` (default: `"nats://nats:4222"`)
`NATS_NKEYS_IMPORT_DIR` (default: `".nats/"`, )
`NATS_NKEYS_EXPORT_DIR` (default: `".nats/"`)
`NATS_NKEYS_OPERATOR_NAME` (default: `"DjangoOperator"`)

### Retry Mode

`NATS_NSC_RETRY_MODE` (default "STRICT", allowed values: "STRICT" or "IDEMPOTENT")

In `STRICT` mode, `django_nats_nkey.errors.NscConflict` will be raised if `nsc add ...` command returns an "already exists" error. You are responsible for implementing a separate process to handle eventual consistency between Django models and nsc environment.

In `IDEMPOTENT` mode, conflict is logged at the WARNING level but no `Exception` is raised. In this mode, `nsc add` command may be retried many times and will be a no-op if resource already exists.


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


### App Models

`NATS_APP_MODELS` (default: `[ "django_nats_nkey.NatsOrganizationApp" , "django_nats_nkeys.NatsRobotApp" ]`)