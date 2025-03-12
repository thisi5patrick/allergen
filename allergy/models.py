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
