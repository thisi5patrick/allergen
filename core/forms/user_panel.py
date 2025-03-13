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
    )

    class Meta:
        model = SymptomType
        fields = ["name"]

    def __init__(self, *args: Any, **kwargs: Any):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_name(self) -> str:
        name: str = self.cleaned_data["name"]
        if SymptomType.objects.filter(name=name.lower(), user=self.user).exists():
            raise forms.ValidationError("You already have a symptom with this name.")
        return name

    def save(self, commit: bool = True) -> SymptomType:
        instance = super().save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance
