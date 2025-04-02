from typing import Any

from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    common_input_classes = (
        "w-full py-3 pl-10 pr-4 text-gray-700 "
        "bg-gray-100 rounded-lg focus:outline-none focus:ring-2 "
        "focus:ring-purple-600 focus:bg-white"
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

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": common_input_classes,
            },
        ),
    )
    remember_me = forms.BooleanField(
        required=False,
        label="Remember me",
        widget=forms.CheckboxInput(
            attrs={
                "class": "h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded",
            },
        ),
    )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        if not cleaned_data:
            return {}

        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Incorrect username or password. Please try again.")
            cleaned_data["user"] = user

        return cleaned_data
