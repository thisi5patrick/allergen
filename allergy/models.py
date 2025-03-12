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
    UUIDField,
)


class TimestampedModelMixin(Model):
    updated_at = DateTimeField(null=True, auto_now=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class AllergyEntry(TimestampedModelMixin):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = ForeignKey(User, on_delete=CASCADE)
    entry_date = DateField()

    def __str__(self) -> str:
        return f"{self.user} - {self.entry_date}"


class SymptomType(TimestampedModelMixin):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = CharField(max_length=255)
    user = ForeignKey(User, on_delete=CASCADE)

    def __str__(self) -> str:
        return self.name


class SymptomRecord(TimestampedModelMixin):
    uuid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symptom_type = ForeignKey(SymptomType, on_delete=CASCADE, related_name="symptom_records")
    intensity = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    entry = ForeignKey(AllergyEntry, on_delete=CASCADE, related_name="symptom_records")

    def __str__(self) -> str:
        return f"{self.symptom_type.name} - {self.intensity}"
