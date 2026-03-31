"""
Stub migration: consolidated initial state for django_utils tables.
Creates UserFile and OperationLog so that 0004 (which depends on this) can run.
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="uploads/%Y/%m/%d/")),
                ("original_name", models.CharField(max_length=255)),
                ("size", models.BigIntegerField(default=0)),
                ("content_type", models.CharField(blank=True, default="", max_length=127)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "uploader",
                    models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_files",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OperationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(blank=True, default="", max_length=64)),
                ("remark", models.CharField(blank=True, default="", max_length=255)),
                ("path", models.CharField(blank=True, default="", max_length=255)),
                ("method", models.CharField(blank=True, default="", max_length=10)),
                ("ip", models.CharField(blank=True, max_length=64, null=True)),
                ("status_code", models.IntegerField(blank=True, null=True)),
                ("response_code", models.IntegerField(blank=True, null=True)),
                ("success", models.BooleanField(default=True)),
                ("detail", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "operator",
                    models.ForeignKey(
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="operation_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
