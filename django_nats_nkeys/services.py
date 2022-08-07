import subprocess
from typing import List, Union
import logging
import json
import os
from organizations.utils import model_field_names, create_organization
from django.contrib.auth import get_user_model
from django_nats_nkeys.models import NatsOrganizationUser
from django_nats_nkeys.settings import nats_nkeys_settings
from coolname import generate_slug


logger = logging.getLogger(__name__)

User = get_user_model()
NatsOrganization = nats_nkeys_settings.get_nats_account_model()
NatsApp = nats_nkeys_settings.get_nats_app_model()


def run_and_log_output(
    cmd: List[str], stdout=True, stderr=True
) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, capture_output=True, encoding="utf8")
    if result.stdout and stdout:
        logger.info(result.stdout)

    if result.stderr and stderr:
        logger.error(result.stderr)

    result.check_returncode()
    return result


def nsc_init_operator(name, outdir, server, stdout=None, stderr=None) -> str:
    """
    One-time setup of settings.NATS_NKEYS_OPERATOR_NAME
    """
    # create operator with system account
    # https://docs.nats.io/running-a-nats-service/nats_admin/security/jwt#system-account

    # initialize operator
    run_and_log_output(["nsc", "add", "operator", "--name", name, "--sys"])
    # generate a signing key for operator
    run_and_log_output(["nsc", "edit", "operator", "--sk", "generate"])
    # add account-jwt-server-url to operator
    run_and_log_output(["nsc", "edit", "operator", "--account-jwt-server-url", server])

    # set operator context and generate config
    filename = os.path.join(outdir, f"{name}.conf")
    run_and_log_output(
        [
            "nsc",
            "generate",
            "config",
            "--force",
            "--nats-resolver",
            "--config-file",
            filename,
        ]
    )
    return filename


def nsc_push_org(org: NatsOrganization) -> subprocess.CompletedProcess:
    # push to remote
    return run_and_log_output(
        [
            "nsc",
            "push",
            "-a",
            org.name,
            "--account-jwt-server-url",
            nats_nkeys_settings.NATS_SERVER_URI,
        ]
    )


def create_nats_sk_service(
    org: NatsOrganization, role: str = "service"
) -> NatsOrganization:
    """
    Add signing key to NATS account with --role <role>

    The service designing key may be used as a permissions delegate, managing authorizations of all app/users credentials signed by service key
    """
    run_and_log_output(
        [
            "nsc",
            "edit",
            "signing-key",
            "--account",
            org.name,
            "--role",
            role,
            "--sk",
            org.json["nats"]["signing_keys"][0],
        ]
    )
    # re-run describe to output public signing key fingerprint, public key, claims
    result = run_and_log_output(["nsc", "describe", "account", org.name, "--json"])
    describe_account = json.loads(result.stdout)
    # push to remote
    nsc_push_org(org)
    org.json = describe_account
    org.save()
    return org


def create_nats_account_org(user: User) -> NatsOrganization:
    # create organization
    org = create_organization(
        user,
        generate_slug(3),
        org_user_defaults={"is_admin": True},
        model=nats_nkeys_settings.get_nats_account_model(),
    )
    # create account via nsc (log non-sensitive public key subject)
    run_and_log_output(["nsc", "add", "account", "--name", org.name])
    # generate a signing key for account (log non-sensitive public key subject)
    run_and_log_output(
        ["nsc", "edit", "account", "--name", org.name, "--sk", "generate"]
    )
    # push to remote
    nsc_push_org(org)
    result = run_and_log_output(["nsc", "describe", "account", org.name, "--json"])
    describe_account = json.loads(result.stdout)
    org.json = describe_account
    org.save()

    org = create_nats_sk_service(org)
    # add service for account (log non-sensitive public key subject)
    run_and_log_output(
        [
            "nsc",
            "edit",
            "signing-key",
            "--account",
            org.name,
            "--role",
            "service",
            "--sk",
            describe_account["nats"]["signing_keys"][0],
        ]
    )

    org_user, created = org.get_or_add_user(user)
    # add organization user for account
    run_and_log_output(
        [
            "nsc",
            "add",
            "user",
            "--account",
            org.name,
            "--name",
            org_user.app_name,
            "-K",
            "service",
        ]
    )
    # describe app chain of trust, public signing key fingerprint, public key, claims
    result = run_and_log_output(
        ["nsc", "describe", "user", org_user.app_name, "--json"],
    )
    describe_user = json.loads(result.stdout)
    org_user.json = describe_user
    nsc_push_org(org)
    org_user.save()

    return org


def create_nats_app(
    user: User, org: NatsOrganization, nats_app_class=NatsApp, **kwargs
) -> NatsApp:
    """
    user - an instance of django.contrib.auth.get_user_model()
    org - an instance of django_nats_nkeys.settings.django_nats_nkeys_settings.get_nats_account_model()
    nats_app_class - use a model other than
    ***kwargs - extra kwargs to pass to NatsApp.objects.create
    """
    # create nats app associated with org user
    app_name = generate_slug(3)
    org_user, created = org.get_or_add_user(user)
    # create user for account
    run_and_log_output(
        [
            "nsc",
            "add",
            "user",
            "--account",
            org.name,
            "--name",
            app_name,
            "-K",
            "service",
        ]
    )

    # describe app chain of trust, public signing key fingerprint, public key, claims
    result = run_and_log_output(
        ["nsc", "describe", "user", app_name, "--json"],
    )

    describe_user = json.loads(result.stdout)
    # push to remote
    nsc_push_org(org)
    nats_app = nats_app_class.objects.create(
        app_name=app_name,
        json=describe_user,
        organization_user=org_user,
        organization=org,
        **kwargs,
    )
    return nats_app


def nsc_generate_creds(
    org: NatsOrganization, app: Union[NatsApp, NatsOrganizationUser]
) -> str:
    result = run_and_log_output(
        ["nsc", "generate", "creds", "--account", org.name, "--name", app.app_name],
        stdout=False,  # do not log sensitive credentials to stdout
    )
    return result.stdout
