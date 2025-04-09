from http import HTTPStatus

import pytest
from django.contrib.auth.models import AbstractUser
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from core.forms.login import LoginForm
from tests.conftest import TEST_PASSWORD, TEST_USERNAME

LOGIN_VIEW = reverse("login_view")
LOGIN_PROCESS = reverse("login_process")


@pytest.mark.django_db()
def test_login_view_with_anonymous_user(anonymous_client: Client) -> None:
    # Given

    # When
    response = anonymous_client.get(LOGIN_VIEW)

    # Then
    assert response.status_code == 200

    assertTemplateUsed(response, "login/login.html")

    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)


@pytest.mark.django_db()
def test_login_view_with_authenticated_user(authenticated_client: Client) -> None:
    # Given
    expected_redirect = reverse("dashboard")

    # When
    response = authenticated_client.get(LOGIN_VIEW)

    # Then
    assertRedirects(response, expected_redirect)


@pytest.mark.django_db()
def test_login_view_with_incorrect_rest_method(anonymous_client: Client) -> None:
    # Given

    # WHen
    response = anonymous_client.post(LOGIN_VIEW, {})

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("remember_me_payload_value", "expected_expiry_age"),
    [
        ("on", 60 * 60 * 24 * 7),
        (None, 60 * 30),
    ],
)
def test_login_process(remember_me_payload_value: str | None, expected_expiry_age: int, user: AbstractUser) -> None:
    # Given
    expected_redirect = reverse("dashboard")

    payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
    }
    if remember_me_payload_value is not None:
        payload["remember_me"] = remember_me_payload_value

    anonymous_client = Client()
    # When
    response = anonymous_client.post(LOGIN_PROCESS, payload)

    # Then
    assertRedirects(response, expected_redirect)
    session_expiry_age = anonymous_client.session.get_expiry_age()
    assert session_expiry_age == expected_expiry_age

    dashboard_response = anonymous_client.get(expected_redirect)
    assert dashboard_response.status_code == HTTPStatus.OK

    assert dashboard_response.context["user"] == user

    if remember_me_payload_value is None:
        anonymous_client.cookies.pop("sessionid")

        expired_response = anonymous_client.get(expected_redirect)
        assertRedirects(expired_response, LOGIN_VIEW)


@pytest.mark.django_db()
def test_login_process_with_incorrect_data(user: AbstractUser, anonymous_client: Client) -> None:
    # Given
    payload = {
        "username": "some-username",
        "password": "some-password",
    }

    # When
    response = anonymous_client.post(LOGIN_PROCESS, payload)

    # Then
    assertTemplateUsed(response, "login/login_form_partial.html")

    form = response.context["form"]
    assert ["Incorrect username or password. Please try again."] == form.non_field_errors()


@pytest.mark.django_db()
def test_login_process_with_incorrect_rest_method(anonymous_client: Client) -> None:
    # Given

    # WHen
    response = anonymous_client.get(LOGIN_PROCESS)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
def test_login_process_with_missing_payload(anonymous_client: Client) -> None:
    # Given
    payload = {
        "username": "some-username",
    }

    # When
    response = anonymous_client.post(LOGIN_PROCESS, payload)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "login/login_form_partial.html")

    form = response.context["form"]
    assert "This field is required." in form.errors["password"]
