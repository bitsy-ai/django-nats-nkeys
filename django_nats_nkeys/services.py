import subprocess
import json
import os
from organizations.utils import create_organization
from django.contrib.auth import get_user_model
from django_nats_nkeys.models import (
    NatsOrganization,
    NatsOrganization,
    NatsOrganizationUser,
    NatsApp,
)
from django_nats_nkeys.settings import nats_nkeys_settings
from coolname import generate_slug


User = get_user_model()


def init_nsc_operator(name, outdir, server, stdout=None, stderr=None):
    # create operator with system account
    # https://docs.nats.io/running-a-nats-service/nats_admin/security/jwt#system-account
    result = subprocess.run(
        f"nsc add operator --name {name} --sys",
        capture_output=True,
        encoding="utf8",
        shell=True,
    )
    if result.stderr and stderr:
        stderr.write(result.stderr)
    if result.stdout and stdout:
        stdout.write(result.stdout)
    result.check_returncode()

    # generate and add signing key for operator
    result = subprocess.run(
        f"nsc edit operator --sk generate",
        capture_output=True,
        encoding="utf8",
        shell=True,
    )
    if result.stderr and stderr:
        stderr.write(result.stderr)
    if result.stdout and stdout:
        stdout.write(result.stdout)
    result.check_returncode()

    # add account-jwt-server-url to operator
    result = subprocess.run(
        f"nsc edit operator --account-jwt-server-url {server}",
        capture_output=True,
        encoding="utf8",
        shell=True,
    )
    if result.stderr and stderr:
        stderr.write(result.stderr)
    if result.stdout and stdout:
        stdout.write(result.stdout)
    result.check_returncode()

    # set operator context and generate config
    filename = os.path.join(outdir, f"{name}.conf")
    result = subprocess.run(
        f"nsc generate config --force --nats-resolver --config-file {filename}",
        capture_output=True,
        encoding="utf8",
        shell=True,
    )

    if result.stderr and stderr:
        stderr.write(result.stderr)

    if result.stdout and stdout:
        stdout.write(result.stdout)


def push_nsc_org(org: NatsOrganization) -> None:
    # push to remote
    subprocess.run(
        [
            "nsc",
            "push",
            "-a",
            org.name,
            "--account-jwt-server-url",
            nats_nkeys_settings.NATS_SERVER_URI,
        ],
        check=True,
        capture_output=True,
    )


def create_nats_account_org(user: User) -> NatsOrganization:
    # create organization
    org = create_organization(
        user,
        generate_slug(3),
        org_user_defaults={"is_admin": True},
        org_model=nats_nkeys_settings.get_nats_account_model(),
        org_user_model=nats_nkeys_settings.get_nats_user_model(),
    )
    # create account via nsc
    subprocess.run(
        ["nsc", "add", "account", "--name", org.name], check=True, capture_output=True
    )
    # generate a signing key for account
    subprocess.run(
        ["nsc", "edit", "account", "--name", org.name, "--sk", "generate"],
        check=True,
        capture_output=True,
    )
    # get reference to signing key
    result = subprocess.run(
        ["nsc", "describe", "account", org.name, "--json"],
        check=True,
        encoding="utf8",
        capture_output=True,
    )
    describe_account = json.loads(result.stdout)
    # add service for account
    subprocess.run(
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
    # signing key fingerprint, pubkey, claims payload
    result = subprocess.run(
        ["nsc", "describe", "account", org.name, "--json"],
        check=True,
        encoding="utf8",
        capture_output=True,
    )
    describe_account = json.loads(result.stdout)
    # push to remote
    push_nsc_org(org)
    org.json = describe_account
    org.save()
    return org


def create_nats_app(user: User, org: NatsOrganization) -> NatsApp:
    # create nats app associated with org user
    user_name = generate_slug(3)
    org_user, created = org.get_or_add_user(user)
    # create user for account
    subprocess.run(
        [
            "nsc",
            "add",
            "user",
            "--account",
            org.name,
            "--name",
            user_name,
            "-K",
            "service",
        ],
        check=True,
        capture_output=True,
    )

    # signing key fingerprint, pubkey, claims payload
    result = subprocess.run(
        ["nsc", "describe", "user", user_name, "--json"],
        check=True,
        encoding="utf8",
        capture_output=True,
    )
    describe_user = json.loads(result.stdout)
    # push to remote
    push_nsc_org(org)
    nats_app = NatsApp.objects.create(
        name=user_name, json=describe_user, org_user=org_user, org=org
    )
    return nats_app
