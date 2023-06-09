# Generated by Django 3.2.5 on 2022-07-04 19:47

from django.db import migrations, models
import django.db.models.deletion
import django_migration_linter as linter


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0004_customoncallshift_until'),
    ]

    operations = [
        linter.IgnoreMigration(),
        migrations.CreateModel(
            name='OnCallScheduleWeb',
            fields=[
                ('oncallschedule_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='schedules.oncallschedule')),
                ('time_zone', models.CharField(default='UTC', max_length=100)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('schedules.oncallschedule',),
        ),
        migrations.AddField(
            model_name='customoncallshift',
            name='schedule',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='custom_shifts', to='schedules.oncallschedule'),
        ),
        migrations.AlterField(
            model_name='customoncallshift',
            name='type',
            field=models.IntegerField(choices=[(0, 'Single event'), (1, 'Recurrent event'), (2, 'Rolling users'), (3, 'Override')]),
        ),
    ]
