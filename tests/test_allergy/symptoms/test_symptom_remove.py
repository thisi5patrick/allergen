import uuid
from datetime import date
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from allergy.models import SymptomEntry
from tests.factories.symptom_entry import SymptomEntryFactory
from tests.factories.symptom_type import SymptomTypeFactory

SYMPTOM_REMOVE_URL = "allergy:symptom_remove_partial"
LOGIN_URL_NAME = "login_view"
DASHBOARD_URL_NAME = "allergy:dashboard"


@pytest.mark.django_db()
def test_symptom_remove_anonymous(anonymous_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    entry_date = date(2024, 5, 20)
    entry = SymptomEntryFactory.create(user=user, symptom_type=symptom_type, entry_date=entry_date)

    expected_remove_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
        "symptom_uuid": entry.symptom_type.uuid,
    }
    url = reverse(SYMPTOM_REMOVE_URL, kwargs=expected_remove_url_kwargs)

    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db()
def test_symptom_remove_authenticated_valid(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    entry_date = date(2024, 5, 20)
    entry = SymptomEntryFactory.create(user=user, symptom_type=symptom_type, entry_date=entry_date)

    expected_remove_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
        "symptom_uuid": symptom_type.uuid,
    }
    url = reverse(SYMPTOM_REMOVE_URL, kwargs=expected_remove_url_kwargs)

    assert SymptomEntry.objects.filter(pk=entry.pk).exists()

    # When
    response = authenticated_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/remove_selector.html")

    assert response.context["symptom_type"] == symptom_type
    assert not SymptomEntry.objects.filter(pk=entry.pk).exists()

    assertContains(response, 'hx-swap-oob="true"')
    assertContains(response, f'id="symptom-{symptom_type.uuid}"')
    assertContains(response, "hx-get=")
    assertContains(response, f'<div id="intensity-{symptom_type.uuid}" hx-swap-oob="true"></div>')


@pytest.mark.django_db()
def test_symptom_remove_authenticated_already_removed(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    entry_date = date(2024, 5, 21)

    expected_remove_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
        "symptom_uuid": symptom_type.uuid,
    }
    url = reverse(SYMPTOM_REMOVE_URL, kwargs=expected_remove_url_kwargs)

    assert not SymptomEntry.objects.filter(user=user, entry_date=entry_date, symptom_type=symptom_type).exists()

    # When
    response = authenticated_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/remove_selector.html")
    assert response.context["symptom_type"] == symptom_type
    assertContains(response, 'hx-swap-oob="true"')


@pytest.mark.django_db()
def test_symptom_remove_authenticated_wrong_user_returns_400(
    authenticated_second_user_client: Client, user: User
) -> None:
    # Given
    symptom_type_user1 = SymptomTypeFactory.create(user=user)
    entry_date = date(2024, 5, 20)

    entry_user1 = SymptomEntryFactory.create(user=user, symptom_type=symptom_type_user1, entry_date=entry_date)

    expected_remove_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
        "symptom_uuid": symptom_type_user1.uuid,
    }
    url = reverse(SYMPTOM_REMOVE_URL, kwargs=expected_remove_url_kwargs)

    # When
    response = authenticated_second_user_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid or unknown symptom specified for removal." in response.content
    assert SymptomEntry.objects.filter(pk=entry_user1.pk).exists()


@pytest.mark.django_db()
def test_symptom_remove_authenticated_symptom_type_not_found_returns_400(authenticated_client: Client) -> None:
    # Given
    invalid_uuid = uuid.uuid4()
    entry_date = date(2024, 5, 20)

    expected_remove_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
        "symptom_uuid": invalid_uuid,
    }
    url = reverse(SYMPTOM_REMOVE_URL, kwargs=expected_remove_url_kwargs)

    # When
    response = authenticated_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid or unknown symptom specified for removal." in response.content


@pytest.mark.django_db()
def test_symptom_remove_invalid_date(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)

    expected_remove_url_kwargs = {
        "year": 2024,
        "month": 2,
        "day": 30,
        "symptom_uuid": symptom_type.uuid,
    }
    url = reverse(SYMPTOM_REMOVE_URL, kwargs=expected_remove_url_kwargs)

    # When
    response = authenticated_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid date parameters provided." in response.content


@pytest.mark.django_db()
def test_symptom_remove_get_not_allowed(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    entry_date = date(2024, 5, 20)
    SymptomEntryFactory.create(user=user, symptom_type=symptom_type, entry_date=entry_date)

    expected_remove_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
        "symptom_uuid": symptom_type.uuid,
    }
    url = reverse(SYMPTOM_REMOVE_URL, kwargs=expected_remove_url_kwargs)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
