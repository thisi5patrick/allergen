from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import DateField, DateInput, Form, IntegerField, ModelChoiceField

from allergy.models import AllergyEntry, SymptomRecord, SymptomType


class AddSymptomForm(Form):
    date = DateField()
    symptom_type = ModelChoiceField(queryset=SymptomType.objects.none())
    intensity = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["symptom_type"].queryset = SymptomType.objects.filter(user=self.user).all()  # type: ignore

    def save(self) -> AllergyEntry:
        entry_date = self.cleaned_data["date"]
        symptom_type = self.cleaned_data["symptom_type"]
        intensity = self.cleaned_data["intensity"]

        entry, _ = AllergyEntry.objects.get_or_create(user=self.user, entry_date=entry_date)

        symptom_record, _ = SymptomRecord.objects.update_or_create(
            entry=entry, symptom_type=symptom_type, defaults={"intensity": intensity}
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

        entry = AllergyEntry.objects.filter(user=self.user, entry_date=entry_date).first()
        if entry:
            deleted, _ = SymptomRecord.objects.filter(entry=entry, symptom_type=symptom_type).delete()

            if not entry.symptom_records.exists():
                entry.delete()
