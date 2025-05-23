# Generated by Django 5.1.6 on 2025-03-12 13:09

import uuid

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("allergy", "0002_rename_allergyentries_allergyentry_symptomtype_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="symptomrecord",
            name="entry",
        ),
        migrations.RemoveField(
            model_name="symptomrecord",
            name="symptom_type",
        ),
        migrations.AlterUniqueTogether(
            name="symptomtype",
            unique_together={("name", "user")},
        ),
        migrations.CreateModel(
            name="SymptomEntry",
            fields=[
                ("updated_at", models.DateTimeField(auto_now=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("entry_date", models.DateField()),
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
                    "symptom_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="symptom_entries",
                        to="allergy.symptomtype",
                    ),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "unique_together": {("user", "entry_date", "symptom_type")},
            },
        ),
        migrations.DeleteModel(
            name="AllergyEntry",
        ),
        migrations.DeleteModel(
            name="SymptomRecord",
        ),
    ]
