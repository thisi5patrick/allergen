from typing import Any

from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ChoiceField, DateField, DateInput, Form, IntegerField, NumberInput

from allergy.models import AllergyEntries, AllergySymptoms


class AddSymptomForm(Form):
    date = DateField(
        widget=DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    symptom = ChoiceField(choices=AllergySymptoms.Symptoms.choices, widget=DateInput(attrs={"class": "form-control"}))
    intensity = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], widget=NumberInput(attrs={"class": "form-control"})
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def save(self) -> AllergyEntries:
        entry_date = self.cleaned_data["date"]
        symptom = self.cleaned_data["symptom"]
        intensity = self.cleaned_data["intensity"]

        entry, _ = AllergyEntries.objects.get_or_create(user=self.user, entry_date=entry_date)

        allergy_symptom, _ = AllergySymptoms.objects.update_or_create(
            entry=entry, symptom=symptom, defaults={"intensity": intensity}
        )

        return entry


class DeleteSymptomForm(Form):
    symptom = ChoiceField(choices=AllergySymptoms.Symptoms.choices, widget=DateInput(attrs={"class": "form-control"}))
    date = DateField(widget=DateInput(attrs={"type": "date", "class": "form-control"}))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def delete(self) -> None:
        entry_date = self.cleaned_data["date"]
        symptom = self.cleaned_data["symptom"]

        entry = AllergyEntries.objects.filter(user=self.user, entry_date=entry_date).first()
        if entry:
            deleted, _ = AllergySymptoms.objects.filter(entry=entry, symptom=symptom).delete()

            if not entry.symptoms.exists():
                entry.delete()
