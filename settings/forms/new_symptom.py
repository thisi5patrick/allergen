import re
from typing import Any

from django import forms
from django.core.validators import RegexValidator

from allergy.models import SymptomType


class AddNewSymptomForm(forms.ModelForm[SymptomType]):
    name = forms.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=r"^[A-Za-z\s]+$",
                message="Symptom name should only contain letters and spaces",
                code="invalid_symptom_name",
            )
        ],
        widget=forms.TextInput(
            attrs={
                "class": (
                    "w-full px-3 py-2 border border-gray-300 rounded-md "
                    "focus:outline-none focus:ring-2 focus:ring-purple-500",
                )
            }
        ),
    )

    class Meta:
        model = SymptomType
        fields = ["name"]

    def __init__(self, *args: Any, **kwargs: Any):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_name(self) -> str:
        name_raw: str = self.cleaned_data["name"]
        name_stripped = name_raw.strip()
        name_normalized = re.sub(r"\s{2,}", " ", name_stripped)

        if SymptomType.objects.filter(name__iexact=name_normalized, user=self.user).exists():
            raise forms.ValidationError("You already have a symptom with this name.")

        return name_normalized

    def save(self, commit: bool = True) -> SymptomType:
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance
