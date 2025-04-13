from datetime import date
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects, assertTemplateUsed

from tests.factories.symptom_entry import SymptomEntryFactory
from tests.factories.symptom_type import SymptomTypeFactory

EXISTING_SYMPTOMS_PARTIAL_URL_NAME = "settings:partial_existing_symptoms"
REMOVE_SYMPTOM_PARTIAL_URL_NAME = "settings:partial_symptom_type_remove"
LOGIN_URL_NAME = "login_view"


@pytest.mark.django_db
def test_partial_existing_symptoms_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(EXISTING_SYMPTOMS_PARTIAL_URL_NAME)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_partial_existing_symptoms_no_symptoms(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(EXISTING_SYMPTOMS_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/symptoms/existing_symptoms.html")

    assert len(response.context["symptom_types"]) == 0
    assertContains(response, "You haven't added any symptoms yet.")
    assertNotContains(response, 'id="symptom-type-')


@pytest.mark.django_db
def test_partial_existing_symptoms_with_symptoms(authenticated_client: Client, user: User) -> None:
    # Given
    type_a = SymptomTypeFactory.create(user=user, name="Pollen")
    type_b = SymptomTypeFactory.create(user=user, name="Dust Mites")
    type_c = SymptomTypeFactory.create(user=user, name="Cat Dander")

    SymptomEntryFactory.create(user=user, symptom_type=type_b, entry_date=date(2024, 1, 1))
    SymptomEntryFactory.create(user=user, symptom_type=type_b, entry_date=date(2024, 1, 2))
    SymptomEntryFactory.create(user=user, symptom_type=type_c, entry_date=date(2024, 1, 1))

    url = reverse(EXISTING_SYMPTOMS_PARTIAL_URL_NAME)

    expected_remove_url_a_kwargs = {"symptom_type_uuid": type_a.uuid}
    expected_remove_url_b_kwargs = {"symptom_type_uuid": type_b.uuid}
    expected_remove_url_c_kwargs = {"symptom_type_uuid": type_c.uuid}

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/symptoms/existing_symptoms.html")
    symptom_types_ctx = response.context["symptom_types"]

    assert len(symptom_types_ctx) == 3
    expected_data = [
        {"uuid": type_c.uuid, "name": type_c.name, "entries_count": 1},
        {"uuid": type_b.uuid, "name": type_b.name, "entries_count": 2},
        {"uuid": type_a.uuid, "name": type_a.name, "entries_count": 0},
    ]
    assert list(symptom_types_ctx) == expected_data

    assertContains(response, f'id="symptom-type-{type_a.uuid}"')
    assertContains(response, f"{type_a.name}")
    assertContains(response, "0 Entries")
    assertContains(response, reverse(REMOVE_SYMPTOM_PARTIAL_URL_NAME, kwargs=expected_remove_url_a_kwargs))
    assertContains(response, f'id="symptom-type-{type_b.uuid}"')
    assertContains(response, f"{type_b.name}")
    assertContains(response, "2 Entries")
    assertContains(response, reverse(REMOVE_SYMPTOM_PARTIAL_URL_NAME, kwargs=expected_remove_url_b_kwargs))
    assertContains(response, f'id="symptom-type-{type_c.uuid}"')
    assertContains(response, f"{type_c.name}")
    assertContains(response, "1 Entry")
    assertContains(response, reverse(REMOVE_SYMPTOM_PARTIAL_URL_NAME, kwargs=expected_remove_url_c_kwargs))


@pytest.mark.django_db
def test_partial_existing_symptoms_data_isolation(
    authenticated_client: Client, authenticated_second_user_client: Client, user: User, second_user: User
) -> None:
    # Given
    type_u1 = SymptomTypeFactory.create(user=user, name="User1 Symptom")
    type_u2 = SymptomTypeFactory.create(user=second_user, name="User2 Symptom")
    url = reverse(EXISTING_SYMPTOMS_PARTIAL_URL_NAME)

    # When
    response_user1 = authenticated_client.get(url)

    # Then
    assert response_user1.status_code == HTTPStatus.OK
    symptom_types_u1 = response_user1.context["symptom_types"]
    assert len(symptom_types_u1) == 1
    assert symptom_types_u1[0]["name"] == type_u1.name
    assertContains(response_user1, type_u1.name)
    assertNotContains(response_user1, type_u2.name)

    # When
    response_user2 = authenticated_second_user_client.get(url)

    # Then
    assert response_user2.status_code == HTTPStatus.OK
    symptom_types_u2 = response_user2.context["symptom_types"]
    assert len(symptom_types_u2) == 1
    assert symptom_types_u2[0]["name"] == type_u2.name
    assertNotContains(response_user2, type_u1.name)
    assertContains(response_user2, type_u2.name)


@pytest.mark.django_db
def test_partial_existing_symptoms_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(EXISTING_SYMPTOMS_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
