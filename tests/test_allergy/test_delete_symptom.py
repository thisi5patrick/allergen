from datetime import date
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from allergy.models import AllergyEntry, SymptomRecord, SymptomType
from tests.factories.allergy_entry import AllergyEntryFactory
from tests.factories.symptom_record import SymptomRecordFactory
from tests.factories.symptom_type import SymptomTypeFactory
from tests.factories.user import UserFactory


@pytest.mark.django_db()
def test_delete_symptom_deny_anonymous(anonymous_client: Client) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom")
    login_endpoint = reverse("login")

    # WHEN
    response = anonymous_client.post(endpoint, {})

    # THEN
    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"] == login_endpoint


@pytest.mark.django_db()
def test_delete_symptom_incorrect_method(authenticated_client: Client) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom")

    # WHEN
    response = authenticated_client.get(endpoint)

    # THEN
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
def test_delete_symptom_all_missing_from_payload(authenticated_client: Client) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom")

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
    endpoint = reverse("delete_symptom")

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
def test_delete_symptom_deletes_symptom_record(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom")

    symptom_type_1 = SymptomTypeFactory.create(user=user)
    symptom_type_2 = SymptomTypeFactory.create(user=user)

    intensity = 1

    today = date.today()

    entry = AllergyEntryFactory.create(entry_date=today, user=user)

    SymptomRecordFactory.create(
        symptom_type=symptom_type_1,
        intensity=intensity,
        entry=entry,
    )
    SymptomRecordFactory.create(
        symptom_type=symptom_type_2,
        intensity=intensity,
        entry=entry,
    )

    assert SymptomRecord.objects.count() == 2

    payload = {
        "date": today,
        "symptom_type": symptom_type_1.uuid,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert SymptomRecord.objects.count() == 1
    assert AllergyEntry.objects.count() == 1
    assert SymptomType.objects.count() == 2


@pytest.mark.django_db()
def test_delete_symptom_deletes_allergy_entry(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom")

    symptom_type = SymptomTypeFactory.create(user=user)

    intensity = 1

    today = date.today()

    SymptomRecordFactory.create(
        symptom_type=symptom_type,
        intensity=intensity,
        entry__user=user,
    )

    payload = {
        "date": today,
        "symptom_type": symptom_type.uuid,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.NO_CONTENT
    assert SymptomRecord.objects.count() == 0
    assert AllergyEntry.objects.count() == 0
    assert SymptomType.objects.count() == 1


@pytest.mark.django_db()
def test_delete_symptom_cannot_delete_of_other_user(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("delete_symptom")
    intensity = 1
    today = date.today()

    second_user = UserFactory.create()
    symptom_type_second_user = SymptomTypeFactory.create(user=second_user)

    SymptomRecordFactory.create(
        symptom_type=symptom_type_second_user,
        intensity=intensity,
        entry__user=second_user,
    )

    symptom_type = SymptomTypeFactory.create(user=user)

    SymptomRecordFactory.create(
        symptom_type=symptom_type,
        intensity=intensity,
        entry__user=user,
    )

    payload = {
        "date": today,
        "symptom_type": symptom_type.uuid,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.NO_CONTENT

    assert SymptomRecord.objects.filter(entry__user=second_user).count() == 1
    assert SymptomRecord.objects.filter(entry__user=user).count() == 0

    assert AllergyEntry.objects.filter(user=second_user).count() == 1
    assert AllergyEntry.objects.filter(user=user).count() == 0

    assert SymptomType.objects.filter(user=second_user).count() == 1
    assert SymptomType.objects.filter(user=user).count() == 1
