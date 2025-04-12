from datetime import date
from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

PARTIAL_CALENDAR_VIEW_NAME = "allergy:partial_calendar"
DASHBOARD_VIEW_NAME = "allergy:dashboard"
LOGIN_VIEW_NAME = "login_view"


def calendar_url(year: int, month: int, day: int | None = None) -> str:
    kwargs = {"year": year, "month": month}
    if day is not None:
        kwargs["day"] = day
    return reverse(PARTIAL_CALENDAR_VIEW_NAME, kwargs=kwargs)


@pytest.mark.django_db
def test_dashboard_view_with_anonymous_user(anonymous_client: Client) -> None:
    # Given
    dashboard_url = reverse(DASHBOARD_VIEW_NAME)
    expected_redirect = reverse("login_view")

    # When
    response = anonymous_client.get(dashboard_url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect)


@pytest.mark.django_db
def test_dashboard_view_with_authenticated_user(authenticated_client: Client) -> None:
    # Given
    dashboard_url = reverse(DASHBOARD_VIEW_NAME)

    today = date.today()
    expected_year = today.year
    expected_month = today.month
    expected_day = today.day

    expected_calendar_url = calendar_url(expected_year, expected_month, expected_day)

    # When
    response = authenticated_client.get(dashboard_url)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "base.html")
    assertTemplateUsed(response, "navbar.html")
    assertTemplateUsed(response, "allergy/dashboard.html")

    assertContains(response, f'hx-get="{expected_calendar_url}"')

    assertContains(response, 'id="calendar-container"')
    assertContains(response, 'id="allergy-symptoms"')


@pytest.mark.django_db
def test_dashboard_view_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    dashboard_url = reverse(DASHBOARD_VIEW_NAME)

    # When
    response = authenticated_client.post(dashboard_url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
