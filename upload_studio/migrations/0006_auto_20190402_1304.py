# Generated by Django 2.1.7 on 2019-04-02 11:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('upload_studio', '0005_project_source_torrent'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='project',
            name='finished_datetime',
            field=models.DateTimeField(null=True),
        ),
    ]
