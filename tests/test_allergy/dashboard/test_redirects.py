import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db()
def test_redirects_to_dashboard_path(authenticated_client: Client) -> None:
    # Given
    url = "/"
    expected_redirect = reverse("allergy:dashboard")

    # When
    response = authenticated_client.get(url)

    # Then
    assertRedirects(response, expected_redirect)
