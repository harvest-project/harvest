# Generated by Django 3.1.2 on 2020-10-18 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('redacted', '0014_auto_20201018_1629'),
    ]

    operations = [
        migrations.RenameField(
            model_name='redactedtorrentgroup',
            old_name='music_info_json',
            new_name='music_info',
        ),
    ]