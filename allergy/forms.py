from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import CharField, DateField, DateInput, Form, IntegerField, ModelChoiceField

from allergy.models import SymptomEntry, SymptomType


class AddSymptomForm(Form):
    selected_date = DateField()
    symptom_uuid = CharField()
    intensity = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_symptom_uuid(self) -> SymptomType:
        symptom_uuid = self.cleaned_data["symptom_uuid"]
        try:
            symptom_type = SymptomType.objects.get(uuid=symptom_uuid, user=self.user)
            return symptom_type
        except SymptomType.DoesNotExist as e:
            raise ValidationError("Invalid symptom type") from e

    def save(self) -> SymptomEntry:
        entry_date = self.cleaned_data["selected_date"]
        symptom_type = self.cleaned_data["symptom_uuid"]
        intensity = self.cleaned_data["intensity"]

        entry, _ = SymptomEntry.objects.update_or_create(
            user=self.user,
            entry_date=entry_date,
            symptom_type=symptom_type,
            defaults={"intensity": intensity},
        )

        return entry


class DeleteSymptomForm(Form):
    symptom_type = ModelChoiceField(queryset=SymptomType.objects.none())
    date = DateField(widget=DateInput())

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["symptom_type"].queryset = SymptomType.objects.filter(user=self.user).all()  # type: ignore

    def delete(self) -> None:
        entry_date = self.cleaned_data["date"]
        symptom_type = self.cleaned_data["symptom_type"]

        SymptomEntry.objects.filter(entry_date=entry_date, symptom_type=symptom_type).delete()
