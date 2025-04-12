import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db()
def test_logout_redirect_with_anonymous_user(anonymous_client: Client) -> None:
    # Given
    url = reverse("logout_process")
    expected_redirect_url = reverse("login_view")

    # When
    response = anonymous_client.post(url, {})

    # Then
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db()
def test_logout_redirect_with_authenticated_user(authenticated_client: Client) -> None:
    # Given
    url = reverse("logout_process")
    expected_redirect_url = reverse("login_view")
    dashboard_url = reverse("allergy:dashboard")

    # When
    response = authenticated_client.post(url, {})

    # Then
    assertRedirects(response, expected_redirect_url)

    dashboard_response = authenticated_client.get(dashboard_url)
    assertRedirects(response, expected_redirect_url)

    assert dashboard_response.context is None
