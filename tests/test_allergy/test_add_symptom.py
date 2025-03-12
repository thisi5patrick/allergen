from datetime import date
from http import HTTPStatus
from typing import Any, Callable, cast

import pytest
from django.contrib.auth.models import User
from django.template import RequestContext
from django.test import Client
from django.urls import reverse

from allergy.models import AllergyEntry, SymptomRecord, SymptomType
from tests.factories.symptom_record import SymptomRecordFactory
from tests.factories.symptom_type import SymptomTypeFactory


@pytest.fixture()
def create_symptom_type() -> Callable[[], SymptomType]:
    def _create_symptom_type() -> SymptomType:
        from tests.factories.symptom_type import SymptomTypeFactory

        return SymptomTypeFactory.create()

    return _create_symptom_type


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
    assert "This field is required." in form.errors["symptom_type"]
    assert "This field is required." in form.errors["intensity"]


@pytest.mark.django_db()
def test_add_symptom_some_missing_from_payload(authenticated_client: Client, user: User) -> None:
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
    assert "This field is required." in form.errors["symptom_type"]


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("payload_factory", "field", "expected_error"),
    [
        (
            lambda create_symptom_type: {
                "date": "incorrect_format",
                "symptom_type": create_symptom_type().name,
                "intensity": 1,
            },
            "date",
            "Enter a valid date.",
        ),
        (
            lambda create_symptom_type: {
                "date": date.today(),
                "symptom_type": "not-a-valid-uuid",
                "intensity": 1,
            },
            "symptom_type",
            "“not-a-valid-uuid” is not a valid UUID.",
        ),
        (
            lambda create_symptom_type: {
                "date": date.today(),
                "symptom_type": create_symptom_type().name,
                "intensity": 0,
            },
            "intensity",
            "Ensure this value is greater than or equal to 1.",
        ),
        (
            lambda create_symptom_type: {
                "date": date.today(),
                "symptom_type": create_symptom_type().name,
                "intensity": 15,
            },
            "intensity",
            "Ensure this value is less than or equal to 10.",
        ),
    ],
)
def test_add_symptom_incorrect_form_of_payload(
    payload_factory: Callable[[Any], dict[Any, Any]],
    field: str,
    expected_error: str,
    authenticated_client: Client,
    create_symptom_type: Callable[[], SymptomType],
) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")
    payload = payload_factory(create_symptom_type)

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    form = response.context["form"]
    assert form.errors[field] == [expected_error]

    context = cast(RequestContext, response.context)
    assert context.template_name == "allergy/partials/symptom_error.html"


@pytest.mark.django_db()
def test_add_symptom_does_not_duplicate_allergy_symptom(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    symptom_type = SymptomTypeFactory.create()
    intensity = 1

    SymptomRecordFactory.create(
        symptom_type=symptom_type,
        intensity=intensity,
        entry__user=user,
    )

    assert SymptomRecord.objects.count() == 1

    payload = {
        "date": date.today(),
        "intensity": intensity,
        "symptom_type": symptom_type,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    context = cast(RequestContext, response.context)
    assert context.template_name == "allergy/partials/symptom_error.html"

    assert SymptomRecord.objects.count() == 1
    assert AllergyEntry.objects.count() == 1


@pytest.mark.django_db()
def test_add_symptom_creates_allergy_entry(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    symptom_type = SymptomTypeFactory.create(user=user)
    intensity = 1

    SymptomRecordFactory.create(
        symptom_type=symptom_type,
        intensity=intensity,
        entry__user=user,
    )

    assert SymptomRecord.objects.count() == 1

    allergy_entry = AllergyEntry.objects.first()

    assert allergy_entry is not None
    allergy_entry.delete()
    assert AllergyEntry.objects.count() == 0

    payload = {
        "date": date.today(),
        "intensity": intensity,
        "symptom_type": symptom_type.uuid,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK

    context = cast(RequestContext, response.context)
    assert context.template_name == "allergy/partials/allergy_symptoms.html"

    assert SymptomRecord.objects.count() == 1
    assert AllergyEntry.objects.count() == 1


@pytest.mark.django_db()
def test_add_symptom_creates_multiple_allergy_symptoms(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    symptom_1 = SymptomTypeFactory.create(user=user)
    payload_1 = {
        "date": date.today(),
        "intensity": 1,
        "symptom_type": symptom_1.uuid,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload_1)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert AllergyEntry.objects.count() == 1
    assert SymptomType.objects.count() == 1
    assert SymptomRecord.objects.count() == 1

    # WHEN
    symptom_2 = SymptomTypeFactory.create(user=user)
    payload_2 = {
        "date": date.today(),
        "intensity": 1,
        "symptom_type": symptom_2.uuid,
    }

    response = authenticated_client.post(endpoint, payload_2)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert AllergyEntry.objects.count() == 1
    assert SymptomRecord.objects.count() == 2
    assert SymptomType.objects.count() == 2


@pytest.mark.django_db()
def test_add_symptom_updates_allergy_symptoms(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("add_symptom")

    symptom_type = SymptomTypeFactory.create(user=user)

    SymptomRecordFactory.create(
        symptom_type=symptom_type,
        intensity=1,
        entry__user=user,
    )

    new_intensity = 5
    payload = {
        "date": date.today(),
        "intensity": new_intensity,
        "symptom_type": symptom_type.uuid,
    }

    # WHEN
    response = authenticated_client.post(endpoint, payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert SymptomRecord.objects.count() == 1

    allergy_symptom = SymptomRecord.objects.first()

    assert allergy_symptom is not None
    assert allergy_symptom.symptom_type == symptom_type
    assert allergy_symptom.intensity == new_intensity
