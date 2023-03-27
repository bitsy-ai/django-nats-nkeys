# Generated by Django 3.2.7 on 2022-08-07 20:36

from django.db import migrations, models
import django_nats_nkeys.models


class Migration(migrations.Migration):
    dependencies = [
        ("django_nats_nkeys", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="natsapp",
            name="unique_app_name_per_org_user",
        ),
        migrations.RemoveField(
            model_name="natsapp",
            name="name",
        ),
        migrations.AddField(
            model_name="natsapp",
            name="app_name",
            field=models.CharField(
                default=django_nats_nkeys.models._default_name, max_length=255
            ),
        ),
        migrations.AddField(
            model_name="natsorganizationuser",
            name="app_name",
            field=models.CharField(
                default=django_nats_nkeys.models._default_name, max_length=255
            ),
        ),
        migrations.AddField(
            model_name="natsorganizationuser",
            name="json",
            field=models.JSONField(
                default=dict,
                help_text="Output of `nsc describe account`",
                max_length=255,
            ),
        ),
        migrations.AddConstraint(
            model_name="natsapp",
            constraint=models.UniqueConstraint(
                fields=("app_name", "organization_user"),
                name="unique_app_name_per_org_user",
            ),
        ),
    ]
