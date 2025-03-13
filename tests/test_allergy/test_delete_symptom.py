from datetime import date, timedelta
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from allergy.models import SymptomEntry, SymptomType
from tests.factories.symptom_entry import SymptomEntryFactory
from tests.factories.symptom_type import SymptomTypeFactory
from tests.factories.user import UserFactory


@pytest.mark.django_db()
def test_delete_symptom(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom_partial")

    symptom_type = SymptomTypeFactory.create(user=user)

    intensity = 1

    today = date.today()

    SymptomEntryFactory.create(
        symptom_type=symptom_type,
        intensity=intensity,
        entry_date=today,
    )

    payload = {
        "date": today,
        "symptom_type": symptom_type.uuid,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert SymptomEntry.objects.count() == 0
    assert SymptomType.objects.count() == 1


@pytest.mark.django_db()
def test_delete_symptom_for_the_exact_day(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom_partial")

    symptom_type = SymptomTypeFactory.create(user=user)

    intensity = 1

    today = date.today()
    yesterday = today - timedelta(days=1)

    SymptomEntryFactory.create(
        symptom_type=symptom_type,
        intensity=intensity,
        entry_date=today,
    )
    SymptomEntryFactory.create(
        symptom_type=symptom_type,
        intensity=intensity,
        entry_date=yesterday,
    )

    payload = {
        "date": today,
        "symptom_type": symptom_type.uuid,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert SymptomEntry.objects.count() == 1
    assert SymptomType.objects.count() == 1


@pytest.mark.django_db()
def test_delete_symptom_deny_anonymous(anonymous_client: Client) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom_partial")
    login_endpoint = reverse("login_view")

    # WHEN
    response = anonymous_client.post(endpoint, {})

    # THEN
    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"] == login_endpoint


@pytest.mark.django_db()
def test_delete_symptom_incorrect_method(authenticated_client: Client) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom_partial")

    # WHEN
    response = authenticated_client.get(endpoint)

    # THEN
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
def test_delete_symptom_all_missing_from_payload(authenticated_client: Client) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom_partial")

    # WHEN
    response = authenticated_client.post(endpoint, {})

    # THEN
    assert response.status_code == HTTPStatus.OK

    form = response.context["form"]

    assert "This field is required." in form.errors["date"]
    assert "This field is required." in form.errors["symptom_type"]


@pytest.mark.django_db()
def test_delete_symptom_some_missing_from_payload(authenticated_client: Client) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom_partial")

    payload = {
        "date": date.today(),
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    form = response.context["form"]

    assert "date" not in form.errors
    assert "This field is required." in form.errors["symptom_type"]


@pytest.mark.django_db()
def test_delete_symptom_cannot_delete_of_other_user(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom_partial")
    intensity = 1
    today = date.today()

    second_user = UserFactory.create()
    symptom_type_second_user = SymptomTypeFactory.create(user=second_user)

    SymptomEntryFactory.create(
        symptom_type=symptom_type_second_user,
        intensity=intensity,
        user=second_user,
    )

    symptom_type = SymptomTypeFactory.create(user=user)

    SymptomEntryFactory.create(
        symptom_type=symptom_type,
        intensity=intensity,
        user=user,
    )

    payload = {
        "date": today,
        "symptom_type": symptom_type.uuid,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.NO_CONTENT

    assert SymptomEntry.objects.filter(user=second_user).count() == 1
    assert SymptomEntry.objects.filter(user=user).count() == 0

    assert SymptomType.objects.filter(user=second_user).count() == 1
    assert SymptomType.objects.filter(user=user).count() == 1
