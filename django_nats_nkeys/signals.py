from django.dispatch import receiver
from django.db.models.signals import m2m_changed

from .services import run_nsc_and_log_output, save_describe_json
from .models import NatsMessageExport
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

        # add export to account associated with NatsOrganization
        run_nsc_and_log_output(cmd)

        # update NatsOrganization json
        save_describe_json(instance.name, instance)
