from django.dispatch import receiver
from django.db.models.signals import m2m_changed

from .services import nsc_add_import, run_nsc_and_log_output, save_describe_json
from .models import NatsMessageExport, NatsMessageExportType
from .settings import nats_nkeys_settings

NatsOrganization = nats_nkeys_settings.get_nats_account_model()


@receiver(m2m_changed, sender=NatsOrganization.exports.through)
def add_nats_organization_export(sender, instance, model, action, pk_set, **kwargs):
    """
    sender - NatsOrganization.exports.through (intermediate M2M model) class
    instance - NatsOrganization
    model - NatsMessageExport
    """

    if action == "post_add":
        # nsc add export for NatsOrganization account
        msg_export_id = pk_set.pop()
        msg_export = model.objects.get(id=msg_export_id)
        cmd = [
            "nsc",
            "add",
            "export",
            "--account",
            instance.name,
            "--subject",
            msg_export.subject_pattern,
            "--name",
            msg_export.name,
        ]

        # is export private?
        if msg_export.public is False:
            cmd += ["--private"]

        # is export a service?
        if msg_export.export_type == NatsMessageExportType.SERVICE:
            cmd += ["--service"]

        # add export to account associated with NatsOrganization
        run_nsc_and_log_output(cmd)

        # update NatsOrganization json
        save_describe_json(instance.name, instance)

        # handle import for x-account orgs
        for org_account in msg_export.nats_organization_imports.all():
            nsc_add_import(
                instance.name,
                org_account.name,
                msg_export.subject_pattern,
                public=msg_export.public,
            )
            save_describe_json(org_account.name, org_account)

        # handle import for robot account
        for robot_account in msg_export.nats_robot_imports.all():
            nsc_add_import(
                instance.name,
                robot_account.name,
                msg_export.subject_pattern,
                public=msg_export.public,
            )
            save_describe_json(robot_account.name, robot_account)
