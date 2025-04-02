from typing import Any, cast

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible


class RegistrationForm(forms.Form):
    common_input_classes = (
        "w-full py-3 pl-10 pr-4 text-gray-700 bg-gray-100 "
        "rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 "
        "focus:bg-white"
    )

    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": common_input_classes,
                "placeholder": "Username",
            }
        ),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": common_input_classes,
            },
        ),
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": common_input_classes,
            },
        ),
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": common_input_classes,
            },
        ),
    )
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
            self.add_error("password", "Passwords do not match.")

        try:
            validate_password(password1)
        except ValidationError as e:
            self.add_error("password", e)

        return cleaned_data
