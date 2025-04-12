import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db()
def test_404_redirect_with_anonymous_user(anonymous_client: Client) -> None:
    # Given
    url = "/some-non-existent-url/"
    expected_redirect_url = reverse("login_view")

    # When
    response = anonymous_client.get(url)

    # Then
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db()
def test_404_redirect_with_authenticated_user(authenticated_client: Client) -> None:
    # Given
    url = "/some-non-existent-url/"
    expected_redirect_url = reverse("allergy:dashboard")

    # When
    response = authenticated_client.get(url)

    # Then
    assertRedirects(response, expected_redirect_url)
