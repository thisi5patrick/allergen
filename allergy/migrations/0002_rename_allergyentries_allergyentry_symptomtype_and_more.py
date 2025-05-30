# Generated by Django 5.1.6 on 2025-03-10 17:41

import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("allergy", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AllergyEntries",
            new_name="AllergyEntry",
        ),
        migrations.CreateModel(
            name="SymptomType",
            fields=[
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SymptomRecord",
            fields=[
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
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
                        related_name="symptom_records",
                        to="allergy.allergyentry",
                    ),
                ),
                (
                    "symptom_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="symptom_records",
                        to="allergy.symptomtype",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.DeleteModel(
            name="AllergySymptoms",
        ),
    ]
