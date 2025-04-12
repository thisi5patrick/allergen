from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from core.forms.login import LoginForm
from tests.conftest import TEST_PASSWORD_1, TEST_USERNAME_1

LOGIN_VIEW_NAME = "login_view"
LOGIN_PROCESS_NAME = "login_process"
DASHBOARD_VIEW_NAME = "allergy:dashboard"


@pytest.mark.django_db()
def test_login_view_with_anonymous_user(anonymous_client: Client) -> None:
    # Given
    url = reverse(LOGIN_VIEW_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == 200

    assertTemplateUsed(response, "login/login.html")

    assert "form" in response.context
    assert isinstance(response.context["form"], LoginForm)


@pytest.mark.django_db()
def test_login_view_with_authenticated_user(authenticated_client: Client) -> None:
    # Given
    url = reverse(LOGIN_VIEW_NAME)
    expected_redirect = reverse(DASHBOARD_VIEW_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assertRedirects(response, expected_redirect)


@pytest.mark.django_db()
def test_login_view_with_incorrect_rest_method(anonymous_client: Client) -> None:
    # Given
    url = reverse(LOGIN_VIEW_NAME)

    # WHen
    response = anonymous_client.post(url, {})

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
def test_login_process(remember_me_payload_value: str | None, expected_expiry_age: int, user: User) -> None:
    # Given
    url = reverse(LOGIN_PROCESS_NAME)
    expected_redirect = reverse(DASHBOARD_VIEW_NAME)
    expected_redirect_for_expired_session = reverse(LOGIN_VIEW_NAME)

    payload = {
        "username": TEST_USERNAME_1,
        "password": TEST_PASSWORD_1,
    }
    if remember_me_payload_value is not None:
        payload["remember_me"] = remember_me_payload_value

    anonymous_client = Client()
    # When
    response = anonymous_client.post(url, payload)

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
        assertRedirects(expired_response, expected_redirect_for_expired_session)


@pytest.mark.django_db()
def test_login_process_with_incorrect_data(user: User, anonymous_client: Client) -> None:
    # Given
    url = reverse(LOGIN_PROCESS_NAME)

    payload = {
        "username": "some-username",
        "password": "some-password",
    }

    # When
    response = anonymous_client.post(url, payload)

    # Then
    assertTemplateUsed(response, "login/login_form_partial.html")

    form = response.context["form"]
    assert ["Incorrect username or password. Please try again."] == form.non_field_errors()


@pytest.mark.django_db()
def test_login_process_with_incorrect_rest_method(anonymous_client: Client) -> None:
    # Given
    url = reverse(LOGIN_PROCESS_NAME)

    # WHen
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
def test_login_process_with_missing_payload(anonymous_client: Client) -> None:
    # Given
    url = reverse(LOGIN_PROCESS_NAME)

    payload = {
        "username": "some-username",
    }

    # When
    response = anonymous_client.post(url, payload)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "login/login_form_partial.html")

    form = response.context["form"]
    assert "This field is required." in form.errors["password"]
