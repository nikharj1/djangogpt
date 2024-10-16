# Generated by Django 4.2.16 on 2024-10-15 06:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="chat_history",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_message", models.TextField()),
                ("bot_response", models.TextField()),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "image_path",
                    models.FileField(blank=True, null=True, upload_to="Bot_Response"),
                ),
                (
                    "input_image",
                    models.FileField(blank=True, null=True, upload_to="User_Uploaded"),
                ),
                ("username", models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]