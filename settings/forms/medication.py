from typing import Any, cast

from django.contrib.auth.models import User
from django.forms import ChoiceField, ModelForm
from django.forms.widgets import Select, TextInput

from allergy.models import Medication


class AddMedicationForm(ModelForm[Medication]):
    medication_type = ChoiceField(
        choices=Medication.MedicationType.choices,
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
        model = Medication
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

        medication_type = cleaned_data.get("medication_type")
        medication_name = cleaned_data.get("medication_name")

        if medication_name and medication_type and self.user:
            queryset = Medication.objects.filter(
                medication_name__iexact=medication_name, medication_type=medication_type, user=self.user
            )

            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                self.add_error("medication_name", "This medication with the same type already exists for you.")

        return cleaned_data

    def save(self, commit: bool = True) -> Medication:
        instance = super().save(False)
        instance.user = cast(User, self.user)
        if commit:
            instance.save()

        return instance
