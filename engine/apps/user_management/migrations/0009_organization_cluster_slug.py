# Generated by Django 3.2.18 on 2023-03-08 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_management', '0008_organization_is_grafana_incident_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='cluster_slug',
            field=models.CharField(default=None, max_length=300, null=True),
        ),
    ]
