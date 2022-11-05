# Generated by Django 3.2.16 on 2022-11-05 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_nats_nkeys', '0008_auto_20221105_0256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='natsorganizationapp',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='django_nats_nkeys_natsorganizationapp', to='django_nats_nkeys.natsorganization'),
        ),
        migrations.AlterField(
            model_name='natsorganizationapp',
            name='organization_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='django_nats_nkeys_natsorganizationapp', to='django_nats_nkeys.natsorganizationuser'),
        ),
    ]
