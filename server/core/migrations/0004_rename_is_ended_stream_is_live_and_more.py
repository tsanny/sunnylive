# Generated by Django 5.0.6 on 2024-06-28 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_stream_stream_key"),
    ]

    operations = [
        migrations.RenameField(
            model_name="stream", old_name="is_ended", new_name="is_live",
        ),
        migrations.RemoveField(model_name="stream", name="is_started",),
    ]