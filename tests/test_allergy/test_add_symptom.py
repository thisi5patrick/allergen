from datetime import date
from http import HTTPStatus
from typing import cast

import pytest
from django.contrib.auth.models import User
from django.template import RequestContext
from django.test import Client
from django.urls import reverse

from allergy.models import AllergyEntries, AllergySymptoms
from tests.factories.allergy_symptoms import AllergySymptomsFactory


@pytest.mark.django_db()
def test_add_symptom_deny_anonymous(anonymous_client: Client) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")
    login_endpoint = reverse("login")

    # WHEN
    response = anonymous_client.post(endpoint, {})

    # THEN
    assert response.status_code == HTTPStatus.FOUND
    assert response["Location"] == login_endpoint


@pytest.mark.django_db()
def test_add_symptom_incorrect_method(authenticated_client: Client) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    # WHEN
    response = authenticated_client.get(endpoint)

    # THEN
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db()
def test_add_symptom_all_missing_from_payload(authenticated_client: Client) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    # WHEN
    response = authenticated_client.post(endpoint, {})

    # THEN
    assert response.status_code == HTTPStatus.OK

    form = response.context["form"]

    assert "This field is required." in form.errors["date"]
    assert "This field is required." in form.errors["symptom"]
    assert "This field is required." in form.errors["intensity"]


@pytest.mark.django_db()
def test_add_symptom_some_missing_from_payload(authenticated_client: Client) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    payload = {
        "date": date.today(),
        "intensity": 1,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    form = response.context["form"]

    assert "date" not in form.errors
    assert "intensity" not in form.errors
    assert "This field is required." in form.errors["symptom"]


@pytest.mark.parametrize(
    ("payload", "field", "expected_error"),
    [
        (
            {
                "date": "incorrect_format",
                "symptom": AllergySymptoms.Symptoms.HEADACHE,
                "intensity": 1,
            },
            "date",
            "Enter a valid date.",
        ),
        (
            {
                "date": date.today(),
                "symptom": "Incorrect symptom",
                "intensity": 1,
            },
            "symptom",
            "Select a valid choice. Incorrect symptom is not one of the available choices.",
        ),
        (
            {
                "date": date.today(),
                "symptom": AllergySymptoms.Symptoms.HEADACHE,
                "intensity": 0,
            },
            "intensity",
            "Ensure this value is greater than or equal to 1.",
        ),
        (
            {
                "date": date.today(),
                "symptom": AllergySymptoms.Symptoms.HEADACHE,
                "intensity": 15,
            },
            "intensity",
            "Ensure this value is less than or equal to 10.",
        ),
    ],
)
@pytest.mark.django_db()
def test_add_symptom_incorrect_form_of_payload(
    payload: dict[str, str], field: str, expected_error: str, authenticated_client: Client
) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    form = response.context["form"]
    assert form.errors[field] == [expected_error]

    context = cast(RequestContext, response.context)
    assert context.template_name == "allergy/partials/add_symptom_error.html"


@pytest.mark.django_db()
def test_add_symptom_does_not_duplicate_allergy_symptom(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    symptom = AllergySymptoms.Symptoms.HEADACHE
    intensity = 1

    AllergySymptomsFactory.create(
        symptom=symptom,
        intensity=intensity,
        entry__user=user,
    )

    assert AllergySymptoms.objects.count() == 1

    payload = {
        "date": date.today(),
        "intensity": intensity,
        "symptom": symptom,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    context = cast(RequestContext, response.context)
    assert context.template_name == "allergy/partials/allergy_symptoms.html"

    assert AllergySymptoms.objects.count() == 1
    assert AllergyEntries.objects.count() == 1


@pytest.mark.django_db()
def test_add_symptom_creates_allergy_entry(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    symptom = AllergySymptoms.Symptoms.HEADACHE
    intensity = 1

    AllergySymptomsFactory.create(
        symptom=symptom,
        intensity=intensity,
        entry__user=user,
    )

    assert AllergySymptoms.objects.count() == 1

    allergy_symptom = AllergyEntries.objects.first()

    assert allergy_symptom is not None
    allergy_symptom.delete()
    assert AllergyEntries.objects.count() == 0

    payload = {
        "date": date.today(),
        "intensity": intensity,
        "symptom": symptom,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    context = cast(RequestContext, response.context)
    assert context.template_name == "allergy/partials/allergy_symptoms.html"

    assert AllergySymptoms.objects.count() == 1
    assert AllergyEntries.objects.count() == 1


@pytest.mark.django_db()
def test_add_symptom_creates_multiple_allergy_symptoms(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    num_of_final_symptoms = 2
    payload_1 = {
        "date": date.today(),
        "intensity": 1,
        "symptom": AllergySymptoms.Symptoms.HEADACHE,
    }
    payload_2 = {
        "date": date.today(),
        "intensity": 1,
        "symptom": AllergySymptoms.Symptoms.ITCHY_EYES,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload_1)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert AllergySymptoms.objects.count() == 1

    assert AllergyEntries.objects.count() == 1

    # WHEN
    response = authenticated_client.post(endpoint, payload_2)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert AllergySymptoms.objects.count() == num_of_final_symptoms

    assert AllergyEntries.objects.count() == 1


@pytest.mark.django_db()
def test_add_symptom_updates_allergy_symptoms(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    symptom = AllergySymptoms.Symptoms.HEADACHE

    AllergySymptomsFactory.create(
        symptom=symptom,
        intensity=1,
        entry__user=user,
    )

    new_intensity = 5
    payload = {
        "date": date.today(),
        "intensity": new_intensity,
        "symptom": symptom,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert AllergySymptoms.objects.count() == 1

    allergy_symptom = AllergySymptoms.objects.first()

    assert allergy_symptom is not None
    assert allergy_symptom.symptom == symptom
    assert allergy_symptom.intensity == new_intensity
