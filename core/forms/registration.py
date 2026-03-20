from typing import Any, cast

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(required=True, widget=forms.PasswordInput())
    captcha = ReCaptchaField(
        widget=ReCaptchaV2Invisible(
            attrs={
                "data-callback": "triggerHtmxSubmit",
                "data-bind": "submit-button",
            }
        )
    )

    def clean_username(self) -> str:
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return cast(str, username)

    def clean_email(self) -> str:
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return cast(str, email)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if not cleaned_data:
            return {}

        password1 = cleaned_data["password"]
        password2 = cleaned_data["password2"]

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")

        try:
            validate_password(password1)
        except ValidationError as e:
            self.add_error("password", e)

        return cleaned_data
