# Generated by Django 5.0.6 on 2024-06-24 07:11

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_rename_user_stream_host"),
    ]

    operations = [
        migrations.AddField(
            model_name="stream",
            name="stream_key",
            field=models.CharField(
                default=core.models.generate_stream_key,
                max_length=16,
                unique=True,
                verbose_name="Stream key",
            ),
        ),
    ]
