from datetime import date
from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from parsel import Selector
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects, assertTemplateUsed

PARTIAL_CALENDAR_VIEW_NAME = "allergy:partial_calendar"
DASHBOARD_VIEW_NAME = "allergy:dashboard"
LOGIN_VIEW_NAME = "login_view"


def calendar_url(year: int, month: int, day: int | None = None) -> str:
    kwargs = {"year": year, "month": month}
    if day is not None:
        kwargs["day"] = day
    return reverse(PARTIAL_CALENDAR_VIEW_NAME, kwargs=kwargs)


@pytest.mark.django_db()
def test_partial_calendar_anonymous_user(anonymous_client: Client) -> None:
    # Given
    url = calendar_url(2024, 5, 15)
    expected_redirect_url = f"{reverse(LOGIN_VIEW_NAME)}"

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db()
def test_partial_calendar_view_with_day(authenticated_client: Client) -> None:
    # Given
    year, month, day = 2024, 4, 15
    url = calendar_url(year, month, day)
    expected_date_string = date(year, month, day).strftime("%Y-%m-%d")
    expected_month_name = "April"

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/calendar/calendar.html")
    assertTemplateUsed(response, "allergy/partials/calendar/calendar_grid.html")

    context = response.context
    assert context["current_year"] == year
    assert context["current_month_num"] == month
    assert context["current_month_name"] == expected_month_name
    assert context["selected_day"] == day
    assert context["selected_date_str"] == expected_date_string

    assert "calendar_matrix" in context
    assert isinstance(context["calendar_matrix"], list)
    assert len(context["calendar_matrix"]) >= 4

    assert "weekdays" in context
    assert context["weekdays"] == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    content = response.content.decode(response.charset)
    selector = Selector(text=content)

    selected_button_xpath = f'//button[normalize-space(.)="{day}"]'
    selected_button = selector.xpath(selected_button_xpath)

    assert len(selected_button) == 1

    button_classes = selected_button.xpath("@class").get()

    assert button_classes is not None
    assert "bg-blue-500" in button_classes.split()


@pytest.mark.django_db()
def test_partial_calendar_view_without_day(authenticated_client: Client) -> None:
    # Given
    year, month = 2024, 6
    url = calendar_url(year, month)
    expected_month_name = "June"

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/calendar/calendar.html")

    context = response.context
    assert context["current_year"] == year
    assert context["current_month_num"] == month
    assert context["current_month_name"] == expected_month_name
    assert context["selected_day"] is None
    assert context["selected_date_str"] is None

    assertNotContains(response, "bg-blue-500", html=True)


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("year", "month", "expected_prev_year", "expected_prev_month"),
    [
        (2024, 5, 2024, 4),
        (2024, 1, 2023, 12),
        (2020, 3, 2020, 2),
    ],
)
def test_partial_calendar_previous_month_logic(
    authenticated_client: Client, year: int, month: int, expected_prev_year: int, expected_prev_month: int
) -> None:
    # Given
    url = calendar_url(year, month)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK

    context = response.context
    assert context["prev_year"] == expected_prev_year
    assert context["prev_month"] == expected_prev_month

    expected_prev_url = calendar_url(expected_prev_year, expected_prev_month)
    assertContains(response, f'hx-get="{expected_prev_url}"')


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("year", "month", "expected_next_year", "expected_next_month"),
    [
        (2024, 5, 2024, 6),
        (2024, 12, 2025, 1),
        (2024, 1, 2024, 2),
        (2020, 2, 2020, 3),
    ],
)
def test_partial_calendar_next_month_logic(
    authenticated_client: Client, year: int, month: int, expected_next_year: int, expected_next_month: int
) -> None:
    # Given
    url = calendar_url(year, month)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK

    context = response.context
    assert context["next_year"] == expected_next_year
    assert context["next_month"] == expected_next_month

    expected_next_url = calendar_url(expected_next_year, expected_next_month)
    assertContains(response, f'hx-get="{expected_next_url}"')


@pytest.mark.django_db()
def test_partial_calendar_htmx_request_renders_correctly(authenticated_client: Client) -> None:
    # Given
    year, month, day = 2024, 7, 4
    url = calendar_url(year, month, day)

    # When
    response = authenticated_client.get(url, HTTP_HX_REQUEST="true")

    # Then
    assert response.status_code == 200
    assertTemplateUsed(response, "allergy/partials/calendar/calendar.html")

    assert response.context["current_year"] == year
    assert response.context["selected_day"] == day


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("year", "month", "day"),
    [
        ("2024", "0", "10"),
        ("2024", "13", "10"),
        ("2024", "4", "31"),
        ("2023", "2", "29"),
        ("2024", "2", "30"),
    ],
)
def test_partial_calendar_invalid_date_value_returns_400(
    authenticated_client: Client, year: str, month: str, day: str | None
) -> None:
    # Given
    url = calendar_url(int(year), int(month), int(day) if day else None)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid date parameters provided." in response.content


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("year", "month", "day"),
    [
        ("a", "5", "10"),
        ("abcd", "5", "10"),
        ("2024", "a", "10"),
        ("2024", "abcd", "10"),
        ("2024", "5", "a"),
        ("2024", "5", "abcd"),
    ],
)
def test_partial_calendar_invalid_format_redirects(
    authenticated_client: Client, year: str, month: str, day: str | None
) -> None:
    # Given
    url = f"/partial/calendar/{year}/{month}/"
    if day is not None:
        url += f"{day}/"

    expected_redirect_url = reverse("allergy:dashboard")

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db()
def test_partial_calendar_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = calendar_url(2024, 8, 1)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
