# Generated by Django 5.1.6 on 2025-03-07 18:39

import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AllergyEntries",
            fields=[
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("entry_date", models.DateField()),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AllergySymptoms",
            fields=[
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "symptom",
                    models.CharField(
                        choices=[
                            ("SNEEZING", "Sneezing"),
                            ("RUNNY_NOSE", "Runny nose"),
                            ("ITCHY_EYES", "Itchy eyes"),
                            ("HEADACHE", "Headache"),
                        ],
                        max_length=255,
                    ),
                ),
                (
                    "intensity",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(10),
                        ]
                    ),
                ),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="symptoms",
                        to="allergy.allergyentries",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
