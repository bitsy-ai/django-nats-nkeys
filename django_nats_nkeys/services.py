import subprocess
import tempfile
from typing import List, Optional, Union, Tuple, Dict, Any
import logging
import json
import os
from organizations.utils import model_field_names
from django.contrib.auth import get_user_model
from django_nats_nkeys.errors import (
    NscConflict,
    NscError,
    NscStreamExportConflict,
)
from django_nats_nkeys.settings import NatsNscRetryMode, nats_nkeys_settings
from coolname import generate_slug

logger = logging.getLogger(__name__)

User = get_user_model()
NatsOrganization = nats_nkeys_settings.get_nats_account_model()
NatsOrganizationUser = nats_nkeys_settings.get_nats_user_model()
NatsOrganizationApp = nats_nkeys_settings.get_nats_organization_app_model()
NatsRobotAccountModel = nats_nkeys_settings.get_nats_robot_account_model()
NatsRobotAppModel = nats_nkeys_settings.get_nats_robot_app_model()


def create_organization(
    user: User,
    name,
    slug=None,
    is_active=None,
    org_defaults=None,
    org_user_defaults=None,
):
    """
    Extends organizations.utils.create_organization to call create_nsc method
    """
    org_model = nats_nkeys_settings.get_nats_account_model()

    org_owner_model = org_model.owner.related.related_model
    org_user_model = org_model.organization_users.rel.related_model

    if org_defaults is None:
        org_defaults = {}
    if org_user_defaults is None:
        if "is_admin" in model_field_names(org_user_model):
            org_user_defaults = {"is_admin": True}
        else:
            org_user_defaults = {}

    if slug is not None:
        org_defaults.update({"slug": slug})
    if is_active is not None:
        org_defaults.update({"is_active": is_active})

    org_defaults.update({"name": name})
    organization = org_model.objects.create_nsc(**org_defaults)

    org_user_defaults.update({"organization": organization, "user": user})
    new_user = org_user_model.objects.create_nsc(**org_user_defaults)

    org_owner_model.objects.create(
        organization=organization, organization_user=new_user
    )
    return organization


def nsc_bearer_auth_enable(app: NatsOrganizationApp):
    run_nsc_and_log_output(
        [
            "nsc",
            "edit",
            "user",
            "--account",
            app.organization.name,
            "--name",
            app.app_name,
            "--bearer",
        ]
    )
    # push local changes to remote NATs resolver
    nsc_push(account=app.organization.name)
    # describe the account and update organization's json representation
    save_describe_json(app.organization.name, app, app_name=app.app_name)


def nsc_jetstream_update(org: NatsOrganization):
    run_nsc_and_log_output(
        [
            "nsc",
            "edit",
            "account",
            "--name",
            org.name,
            "--js-mem-storage",
            org.jetstream_max_mem,
            "--js-disk-storage",
            org.jetstream_max_file,
            "--js-streams",
            str(org.jetstream_max_streams),
            "--js-consumer",
            str(org.jetstream_max_consumers),
        ]
    )
    # push local changes to remote NATs resolver
    nsc_push(account=org.name)

    # describe the account and update organization's json representation
    return save_describe_json(org.name, org)


def nsc_add_account(
    obj: Union[NatsOrganization, NatsRobotAccountModel]
) -> Union[NatsOrganization, NatsRobotAccountModel]:
    # try create nsc account
    run_nsc_and_log_output(["nsc", "add", "account", "--name", obj.name])
    # generate a signing key for account
    run_nsc_and_log_output(
        ["nsc", "edit", "account", "--name", obj.name, "--sk", "generate"]
    )
    # push local changes to remote NATs resolver
    nsc_push(account=obj.name)

    # describe the account and update organization's json representation
    return save_describe_json(obj.name, obj)


def nsc_pull(account=None, force=False) -> subprocess.CompletedProcess:
    cmd = ["nsc", "pull"]
    if account is None:
        cmd.append("--all")
    else:
        cmd.append("--account")
        cmd.append(account)

    if force is True:
        cmd.append("--overwrite-newer")
    extra_args = [
        "--keystore-dir",
        nats_nkeys_settings.NATS_NSC_KEYSTORE_DIR,
        "--config-dir",
        nats_nkeys_settings.NATS_NSC_CONFIG_DIR,
        "--data-dir",
        nats_nkeys_settings.NATS_NSC_DATA_DIR,
    ]
    cmd = cmd + extra_args
    result = subprocess.run(cmd, capture_output=True, encoding="utf8")
    if result.stdout:
        logger.info(result.stdout)

    if result.stderr:
        logger.error(result.stderr)
    result.check_returncode()
    return result


def nsc_push(account=None, force=False) -> subprocess.CompletedProcess:
    cmd = ["nsc", "push"]
    if account is None:
        cmd.append("--all")
    else:
        cmd.append("--account")
        cmd.append(account)
    extra_args = [
        "--keystore-dir",
        nats_nkeys_settings.NATS_NSC_KEYSTORE_DIR,
        "--config-dir",
        nats_nkeys_settings.NATS_NSC_CONFIG_DIR,
        "--data-dir",
        nats_nkeys_settings.NATS_NSC_DATA_DIR,
        "--account-jwt-server-url",
        nats_nkeys_settings.NATS_SERVER_URI,
    ]
    cmd = cmd + extra_args
    result = subprocess.run(cmd, capture_output=True, encoding="utf8")
    if result.stdout:
        logger.info(result.stdout)

    if result.stderr:
        logger.error(result.stderr)
    result.check_returncode()
    return result


class NSCValidator:
    result: Optional[subprocess.CompletedProcess] = None

    def __init__(self, account_name: Optional[str] = None) -> None:
        self.account_name = account_name

    def ok(self) -> bool:
        return self.result.returncode == 0

    def run(self):
        if self.account_name is None:
            cmd = ["nsc", "validate", "--all-accounts"]
        else:
            cmd = ["nsc", "validate", "--account", self.account_name]
        result = run_nsc_and_log_output(cmd, check=False)
        self.result = result


def nsc_validate(account_name: Optional[str] = None) -> NSCValidator:
    validator = NSCValidator(account_name=account_name)
    validator.run()
    return validator


def run_nsc_and_log_output(
    cmd: List[str], stdout=True, stderr=True, check=True
) -> subprocess.CompletedProcess:
    if "nsc" not in cmd:
        raise ValueError(
            "run_nsc_and_log_output is a wrapper for nsc and not intended for general-purpose commands. Received command: %s",
            cmd,
        )
    extra_args = [
        "--keystore-dir",
        nats_nkeys_settings.NATS_NSC_KEYSTORE_DIR,
        "--config-dir",
        nats_nkeys_settings.NATS_NSC_CONFIG_DIR,
        "--data-dir",
        nats_nkeys_settings.NATS_NSC_DATA_DIR,
    ]
    modified_cmd = cmd + extra_args
    logger.info("Running cmd: %s", modified_cmd)
    result = subprocess.run(modified_cmd, capture_output=True, encoding="utf8")
    if result.stdout and stdout:
        logger.info(result.stdout)

    if result.stderr and stderr:
        logger.error(result.stderr)

    if check is True:
        try:
            result.check_returncode()
        except subprocess.CalledProcessError as e:
            # try to convert generic subprocess.CalledProcessError to NscError, or log warning if running in idempotent mode
            if (
                all(el in cmd for el in ["nsc", "add", "export"])
                and "already exports" in result.stderr
            ):
                if nats_nkeys_settings.NATS_NSC_RETRY_MODE == NatsNscRetryMode.STRICT:
                    raise NscStreamExportConflict("Export already exists", e)
                else:
                    logger.warning(
                        "Command %s returned error code %s. Stream export %s already exists.",
                        cmd,
                        e.returncode,
                        e.stderr,
                    )
            elif (
                all(el in cmd for el in ["nsc", "add"])
                and "already exists" in result.stderr
            ):
                if nats_nkeys_settings.NATS_NSC_RETRY_MODE == NatsNscRetryMode.STRICT:
                    raise NscConflict("Account already exists", e)
                else:
                    logger.warning(
                        "Command %s returned error code %s. Resource already exists. %s",
                        cmd,
                        e.returncode,
                        e.stderr,
                    )
            else:
                raise NscError("nsc command exited with non-zero error code", e)
    return result


def nsc_export(dirname: str, force=False) -> subprocess.CompletedProcess:
    cmd = ["nsc", "export", "keys", "--operator", "--dir", dirname]
    if force is True:
        cmd.append("--force")
    return run_nsc_and_log_output(cmd)


def nsc_import(dirname: str) -> subprocess.CompletedProcess:
    run_nsc_and_log_output(["nsc", "import", "keys", "--dir", dirname])


def nsc_init_operator(name, outdir, server) -> str:
    """
    One-time setup of settings.NATS_NKEYS_OPERATOR_NAME
    """
    # create operator with system account
    # https://docs.nats.io/running-a-nats-service/nats_admin/security/jwt#system-account

    # initialize operator
    run_nsc_and_log_output(
        ["nsc", "add", "operator", "--name", name, "--sys", "--generate-signing-key"]
    )
    # add account-jwt-server-url to operator
    run_nsc_and_log_output(
        ["nsc", "edit", "operator", "--account-jwt-server-url", server]
    )

    # set operator context and generate config
    filename = os.path.join(outdir, f"{name}.conf")
    run_nsc_and_log_output(
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


def create_nats_sk_service(
    account_name: str,
    signing_key: str,
    obj: Union[NatsOrganization, NatsRobotAccountModel],
    role: str = "service",
) -> NatsOrganization:
    """
    Add signing key to NATS account with --role <role>

    The service designing key may be used as a permissions delegate, managing authorizations of all app/users credentials signed by service key
    """
    run_nsc_and_log_output(
        [
            "nsc",
            "edit",
            "signing-key",
            "--account",
            account_name,
            "--role",
            role,
            "--sk",
            signing_key,
        ]
    )
    # re-run describe to output public signing key fingerprint, public key, claims
    result = run_nsc_and_log_output(
        ["nsc", "describe", "account", account_name, "--json"]
    )
    describe_account = json.loads(result.stdout)
    # push to remote
    nsc_push(account_name=account_name)
    obj.json = describe_account
    obj.save()
    return obj


def nsc_describe_json(
    account_name: str, app_name: Optional[str] = None
) -> Dict[Any, Any]:

    if app_name is None:
        result = run_nsc_and_log_output(
            ["nsc", "describe", "account", "--name", account_name, "--json"]
        )
    else:
        result = run_nsc_and_log_output(
            [
                "nsc",
                "describe",
                "user",
                "--name",
                app_name,
                "--account",
                account_name,
                "--json",
            ]
        )

    return json.loads(result.stdout)


def save_describe_json(
    account_name: str,
    obj: Union[NatsOrganization, NatsRobotAccountModel, NatsOrganizationUser],
    app_name: Optional[str] = None,
) -> Union[NatsOrganization, NatsRobotAccountModel]:

    obj.json = nsc_describe_json(account_name, app_name=app_name)
    obj.save()
    return obj


def nsc_add_app(
    account_name: str,
    app_name: str,
    obj: Union[NatsOrganizationApp, NatsRobotAppModel],
) -> Union[NatsOrganizationApp, NatsRobotAppModel]:

    run_nsc_and_log_output(
        [
            "nsc",
            "add",
            "user",
            "--account",
            account_name,
            "--name",
            app_name,
        ]
    )

    # update app permissions (if needed)
    base_cmd = ["nsc", "edit", "user", "--account", account_name, "--name", app_name]
    cmd = base_cmd.copy()
    # --allow-pub
    if getattr(obj, "allow_pub", None) is not None:
        cmd += ["--allow-pub", obj.allow_pub]
    # --allow-pubsub
    if getattr(obj, "allow_pubsub", None) is not None:
        cmd += ["--allow-pubsub", obj.allow_pubsub]
    # --allow-sub
    if getattr(obj, "allow_sub", None) is not None:
        cmd += ["--allow-sub", obj.allow_sub]
    # --deny-pub
    if getattr(obj, "deny_pub", None) is not None:
        cmd += ["--deny-pub", obj.deny_pub]
    # --deny-pubsub
    if getattr(obj, "deny_pubsub", None) is not None:
        cmd += ["--deny-pubsub", obj.deny_pubsub]
    # --deny-sub
    if getattr(obj, "deny_sub", None) is not None:
        cmd += ["--deny-sub", obj.deny_pubsub]

    # run edit command if base_cmd has been modified
    if cmd != base_cmd:
        run_nsc_and_log_output(cmd)
    return save_describe_json(account_name, obj, app_name=app_name)


def nsc_generate_creds(account_name: str, app_name: str) -> str:
    result = run_nsc_and_log_output(
        ["nsc", "generate", "creds", "--account", account_name, "--name", app_name],
        stdout=False,  # do not log sensitive credentials to attached stdout logger, just capture and store in memory
    )
    return result.stdout


def nsc_delete_account(account_name: str) -> subprocess.CompletedProcess:
    return run_nsc_and_log_output(["nsc", "delete", "account", account_name])


def nsc_add_import(
    src_account_name: str, dest_account_name: str, subject_pattern: str, public=False
) -> subprocess.CompletedProcess:
    # specify --src-acount and --remote-subject if importing a public stream
    if public is True:
        cmd = [
            "nsc",
            "add",
            "import",
            "--account",
            dest_account_name,
            "--src-account",
            src_account_name,
            "--remote-subject",
            subject_pattern,
        ]
        # add import subject into robot account
        return run_nsc_and_log_output(cmd)
        # for a private export, we must generate an activation token
    else:
        cmd = [
            "nsc",
            "generate",
            "activation",
            "--account",
            src_account_name,
            "--target-account",
            dest_account_name,
            "--subject",
            subject_pattern,
        ]
        # do not log sensitive token to stdout/stderr loggers
        result = run_nsc_and_log_output(cmd, stdout=False, stderr=False)
        activation_token = result.stdout

        # write activation token to NamedTemporaryFile
        with tempfile.NamedTemporaryFile("w+") as f:
            f.write(activation_token)
            f.flush()

            # now, import the stream using the activation token
            # tempfile will automatically be deleted afterwards
            # again, do not log sensitive token stdout/stderr loggers
            cmd = [
                "nsc",
                "add",
                "import",
                "--account",
                dest_account_name,
                "--token",
                f.name,
            ]
            run_nsc_and_log_output(cmd, stdout=False, stderr=False)
