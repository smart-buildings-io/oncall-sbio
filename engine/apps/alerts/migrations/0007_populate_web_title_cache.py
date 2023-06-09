# Generated by Django 3.2.15 on 2022-09-01 16:54

from django.db import migrations

from apps.alerts.models import AlertReceiveChannel
from apps.alerts.tasks import update_web_title_cache_for_alert_receive_channel
import django_migration_linter as linter


def populate_web_title_cache(apps, _):
    pks = AlertReceiveChannel.objects_with_deleted.values_list("pk", flat=True)
    for pk in pks:
        update_web_title_cache_for_alert_receive_channel.delay(pk)


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0006_alertgroup_alerts_aler_channel_ee84a7_idx'),
    ]

    operations = [
        linter.IgnoreMigration(),
        migrations.RenameField(
            model_name='alertgroup',
            old_name='verbose_name',
            new_name='web_title_cache',
        ),
        migrations.RunPython(populate_web_title_cache, migrations.RunPython.noop),
    ]
