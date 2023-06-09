# Generated by Django 3.2.5 on 2022-06-04 10:08

from django.db import migrations, models
import django_migration_linter as linter


class Migration(migrations.Migration):

    dependencies = [
        ('twilioapp', '0001_squashed_initial'),
    ]

    operations = [
        linter.IgnoreMigration(),
        migrations.AddField(
            model_name='phonecall',
            name='grafana_cloud_notification',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='smsmessage',
            name='grafana_cloud_notification',
            field=models.BooleanField(default=False),
        ),
    ]
