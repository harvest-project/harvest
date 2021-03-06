# Generated by Django 2.1.7 on 2019-03-22 23:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bibliotik', '0002_bibliotiktorrent'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bibliotiktorrent',
            old_name='author',
            new_name='joined_authors',
        ),
        migrations.AddField(
            model_name='bibliotiktorrent',
            name='authors_json',
            field=models.TextField(default=[]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bibliotiktorrent',
            name='isbn',
            field=models.CharField(max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='bibliotiktorrent',
            name='pages',
            field=models.IntegerField(null=True),
        ),
    ]
