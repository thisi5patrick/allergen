import uuid

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CharField, IntegerField, Model, TextChoices, UUIDField, CASCADE, ForeignKey, DateField



class AllergiesEntry(Model):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE)
    date = DateField()

    def __str__(self) -> str:
        return f"{self.user} - {self.date}"



class AllergySymptoms(Model):
    class Symptoms(TextChoices):
        SNEEZING = "SNEEZING", "Sneezing"
        RUNNY_NOSE = "RUNNY_NOSE", "Runny nose"
        ITCHY_EYES = "ITCHY_EYES", "Itchy eyes"
        HEADACHE = "HEADACHE", "Headache"

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symptom = CharField(max_length=255, choices=Symptoms.choices)
    intensity = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    entry = ForeignKey(AllergiesEntry, on_delete=CASCADE, related_name='symptoms')

    def __str__(self) -> str:
        return f"{self.symptom} - {self.intensity}"
