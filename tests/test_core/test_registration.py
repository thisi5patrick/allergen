from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from allergy.models import SymptomType
from core.forms.registration import RegistrationForm

REGISTRATION_VIEW_NAME = "registration_view"
REGISTRATION_PROCESS_NAME = "registration_process"
DASHBOARD_VIEW_NAME = "allergy:dashboard"


@pytest.mark.django_db()
def test_registration_view_with_anonymous_user(anonymous_client: Client) -> None:
    # Given
    url = reverse(REGISTRATION_VIEW_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == 200

    assertTemplateUsed(response, "registration/registration.html")

    assert "form" in response.context
    assert isinstance(response.context["form"], RegistrationForm)


@pytest.mark.django_db()
def test_registration_view_with_authenticated_user(authenticated_client: Client) -> None:
    # Given
    url = reverse(REGISTRATION_VIEW_NAME)
    expected_redirect = reverse(DASHBOARD_VIEW_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assertRedirects(response, expected_redirect)


@pytest.mark.django_db()
def test_registration_view_with_incorrect_rest_method(anonymous_client: Client) -> None:
    # Given
    url = reverse(REGISTRATION_VIEW_NAME)

    # WHen
    response = anonymous_client.post(url, {})

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
def test_registration_process(anonymous_client: Client) -> None:
    # Given
    url = reverse(REGISTRATION_PROCESS_NAME)
    expected_redirect = reverse(DASHBOARD_VIEW_NAME)

    payload = {
        "username": "name",
        "email": "email@email.com",
        "password": "some-password-12345",
        "password2": "some-password-12345",
        "g-recaptcha-response": "PASSED",
    }

    # When
    response = anonymous_client.post(url, payload)

    # Then
    assertRedirects(response, expected_redirect)

    assert User.objects.count() == 1

    user = User.objects.first()

    assert SymptomType.objects.filter(user=user).count() == 4
    assert SymptomType.objects.filter(user=user, name="Sneezing").exists()
    assert SymptomType.objects.filter(user=user, name="Runny nose").exists()
    assert SymptomType.objects.filter(user=user, name="Itchy eyes").exists()
    assert SymptomType.objects.filter(user=user, name="Headache").exists()


@pytest.mark.django_db()
def test_registration_process_with_incorrect_rest_method(anonymous_client: Client) -> None:
    # Given
    url = reverse(REGISTRATION_PROCESS_NAME)

    # WHen
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
def test_registration_process_with_missing_payload(anonymous_client: Client) -> None:
    # Given
    url = reverse(REGISTRATION_PROCESS_NAME)
    payload = {
        "email": "email@email.com",
        "password": "password",
        "password2": "password",
    }

    # When
    response = anonymous_client.post(url, payload)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "registration/registration_form_partial.html")

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
    # Given
    url = reverse(REGISTRATION_PROCESS_NAME)

    # When
    response = anonymous_client.post(url, payload)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "registration/registration_form_partial.html")

    form = response.context["form"]
    assert error_message in form.errors[field]


@pytest.mark.django_db()
def test_registration_process_with_already_existing_email(anonymous_client: Client) -> None:
    # Given
    url = reverse(REGISTRATION_PROCESS_NAME)
    existing_email = "some-email@email.com"
    User.objects.create_user(username="some-username", email=existing_email, password="some-password")

    payload = {
        "username": "name",
        "email": existing_email,
        "password": "some-password-12345",
        "password2": "some-password-12345",
        "g-recaptcha-response": "PASSED",
    }

    # When
    response = anonymous_client.post(url, payload)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "registration/registration_form_partial.html")

    form = response.context["form"]
    assert "Email is already registered." in form.errors["email"]


@pytest.mark.django_db()
def test_registration_process_with_already_existing_username(anonymous_client: Client) -> None:
    # Given
    url = reverse(REGISTRATION_PROCESS_NAME)
    existing_username = "some-email@email.com"
    User.objects.create_user(username=existing_username, password="some-password")

    payload = {
        "username": existing_username,
        "email": "email@email.com",
        "password": "some-password-12345",
        "password2": "some-password-12345",
        "g-recaptcha-response": "PASSED",
    }

    # When
    response = anonymous_client.post(url, payload)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "registration/registration_form_partial.html")

    form = response.context["form"]
    assert "Username already exists." in form.errors["username"]
