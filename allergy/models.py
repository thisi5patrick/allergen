import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    CharField,
    DateField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    Model,
    TextChoices,
    UUIDField,
)


class TimestampedModelMixin(Model):
    updated_at = DateTimeField(null=True, auto_now=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AllergyEntries(TimestampedModelMixin):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE)
    entry_date = DateField()

    def __str__(self) -> str:
        return f"{self.user} - {self.entry_date}"


class AllergySymptoms(TimestampedModelMixin):
    class Symptoms(TextChoices):
        SNEEZING = "SNEEZING", "Sneezing"
        RUNNY_NOSE = "RUNNY_NOSE", "Runny nose"
        ITCHY_EYES = "ITCHY_EYES", "Itchy eyes"
        HEADACHE = "HEADACHE", "Headache"

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symptom = CharField(max_length=255, choices=Symptoms.choices)
    intensity = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    entry = ForeignKey(AllergyEntries, on_delete=CASCADE, related_name="symptoms")

    def __str__(self) -> str:
        return f"{self.symptom} - {self.intensity}"
