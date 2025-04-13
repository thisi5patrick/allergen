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


class SymptomType(TimestampedModelMixin):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=255)
    user = ForeignKey(User, on_delete=CASCADE)

    class Meta:
        unique_together = ("name", "user")

    def __str__(self) -> str:
        return self.name


class SymptomEntry(TimestampedModelMixin):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE)
    entry_date = DateField()
    intensity = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    symptom_type = ForeignKey(SymptomType, on_delete=CASCADE, related_name="symptom_entries")

    class Meta:
        unique_together = ("user", "entry_date", "symptom_type")

    def __str__(self) -> str:
        return f"{self.user} - {self.entry_date} - {self.symptom_type.name} ({self.intensity})"


class Medication(TimestampedModelMixin):
    class MedicationType(TextChoices):
        PILLS = "pills", "Pills"
        INJECTION = "injection", "Injection"
        EYE_DROPS = "eye_drops", "Eye Drops"
        NOSE_DROPS = "nose_drops", "Nose Drops"

    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE)
    medication_name = CharField(max_length=255, blank=False)
    medication_type = CharField(max_length=255, choices=MedicationType.choices)

    class Meta:
        unique_together = ("user", "medication_name", "medication_type")

    def __str__(self) -> str:
        return f"{self.user} - {self.medication_name} - {self.medication_type}"

    @staticmethod
    def get_medication_icon_for_type(medication_type_value: str) -> str:
        icons: dict[str, str] = {
            Medication.MedicationType.PILLS: '<i class="fas fa-capsules text-blue-500 mr-2"></i>',
            Medication.MedicationType.INJECTION: '<i class="fas fa-syringe text-red-500 mr-2"></i>',
            Medication.MedicationType.EYE_DROPS: '<i class="fas fa-eye-dropper text-green-500 mr-2"></i>',
            Medication.MedicationType.NOSE_DROPS: '<i class="fas fa-tint text-yellow-500 mr-2"></i>',
        }
        return icons.get(medication_type_value, '<i class="fas fa-question-circle text-gray-500 mr-2"></i>')

    @property
    def icon_html(self) -> str:
        return self.get_medication_icon_for_type(self.medication_type)
