from http import HTTPStatus
from typing import cast

import pytest
from django.contrib.auth.models import User
from django.template import RequestContext
from django.test import Client
from django.urls import reverse

from allergy.models import SymptomType


@pytest.mark.django_db()
def test_registration_process(anonymous_client: Client) -> None:
    # GIVEN
    endpoint = reverse("registration_process")
    payload = {
        "username": "name",
        "email": "email@email.com",
        "password": "password",
        "password2": "password",
    }

    # WHEN
    response = anonymous_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    assert User.objects.count() == 1

    user = User.objects.first()

    assert SymptomType.objects.filter(user=user).count() == 4
    assert SymptomType.objects.filter(user=user, name="Sneezing").exists()
    assert SymptomType.objects.filter(user=user, name="Runny nose").exists()
    assert SymptomType.objects.filter(user=user, name="Itchy eyes").exists()
    assert SymptomType.objects.filter(user=user, name="Headache").exists()


@pytest.mark.django_db()
def test_registration_process_missing_payload(anonymous_client: Client) -> None:
    # GIVEN
    endpoint = reverse("registration_process")
    payload = {
        "email": "email@email.com",
        "password": "password",
        "password2": "password",
    }

    # WHEN
    response = anonymous_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    context = cast(RequestContext, response.context)
    assert context.template_name == "registration/registration_error_message.html"

    form = response.context["form"]
    assert "This field is required." in form.errors["username"]


@pytest.mark.parametrize(
    ("payload", "field", "error_message"),
    [
        (
            {
                "username": "name",
                "email": "email@email.com",
                "password": "password",
                "password2": "mismatching_password",
            },
            "password",
            "Passwords do not match.",
        ),
        (
            {
                "username": "name",
                "email": "incorrect-email",
                "password": "password",
                "password2": "password",
            },
            "email",
            "Enter a valid email address.",
        ),
        (
            {
                "username": "",
                "email": "incorrect-email",
                "password": "password",
                "password2": "password",
            },
            "username",
            "This field is required.",
        ),
    ],
)
@pytest.mark.django_db()
def test_registration_process_incorrect_payload(
    payload: dict[str, str], field: str, error_message: str, anonymous_client: Client
) -> None:
    # GIVEN
    endpoint = reverse("registration_process")

    # WHEN
    response = anonymous_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    context = cast(RequestContext, response.context)
    assert context.template_name == "registration/registration_error_message.html"

    form = response.context["form"]
    assert error_message in form.errors[field]
