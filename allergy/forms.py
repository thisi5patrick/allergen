from typing import Any, cast

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q
from django.forms import CharField, ChoiceField, DateField, DateInput, Form, IntegerField, ModelChoiceField, ModelForm
from django.forms.widgets import Select, TextInput

from allergy.models import Medications, SymptomEntry, SymptomType


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


class MedicationForm(ModelForm[Medications]):
    medication_type = ChoiceField(
        choices=Medications.MedicationType.choices,
        required=True,
        label="Medication Type",
        widget=Select(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 "
                "rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500",
            }
        ),
    )

    class Meta:
        model = Medications
        fields = ["medication_name", "medication_type"]
        widgets = {
            "medication_name": TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md "
                    "focus:outline-none focus:ring-2 focus:ring-purple-500",
                    "placeholder": "Enter medication name",
                    "required": True,
                }
            ),
        }
        labels = {
            "medication_name": "Medication Name",
        }

    def __init__(self, *args: Any, user: User | None = None, **kwargs: Any) -> None:
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if not cleaned_data:
            return {}

        medication_type = cleaned_data["medication_type"]
        medication_name = cleaned_data["medication_name"]

        if Medications.objects.filter(
            Q(medication_name=medication_name) & Q(medication_type=medication_type) & Q(user=self.user)
        ).exists():
            self.add_error("medication_name", "This medication with the same type already exists for you.")

        return cleaned_data

    def save(self, commit: bool = True) -> Medications:
        instance = super().save(False)
        instance.user = cast(User, self.user)
        if commit:
            instance.save(commit)

        return instance
