from typing import Any

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if not cleaned_data:
            return {}

        password1 = cleaned_data["password"]
        password2 = cleaned_data["password2"]

        if password1 and password2 and password1 != password2:
            self.add_error("password", "Passwords do not match.")

        username = cleaned_data.get("username")
        if username and User.objects.filter(username=username).exists():
            self.add_error("username", "Username already exists.")

        email = cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            self.add_error("email", "Email is already registered.")

        try:
            validate_password(password1)
        except ValidationError as e:
            self.add_error("password", e)

        return cleaned_data
