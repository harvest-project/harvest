# Generated by Django 2.1.7 on 2019-04-07 00:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload_studio', '0007_auto_20190405_0248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectstepwarning',
            name='message',
            field=models.TextField(),
        ),
        migrations.AlterUniqueTogether(
            name='projectstepwarning',
            unique_together={('step', 'message')},
        ),
    ]
