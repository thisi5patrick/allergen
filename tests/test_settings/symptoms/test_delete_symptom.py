import uuid
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from allergy.models import SymptomEntry, SymptomType
from tests.factories.symptom_entry import SymptomEntryFactory
from tests.factories.symptom_type import SymptomTypeFactory

REMOVE_SYMPTOM_PARTIAL_URL_NAME = "settings:partial_symptom_type_remove"
LOGIN_URL_NAME = "login_view"
DASHBOARD_URL_NAME = "allergy:dashboard"


@pytest.mark.django_db
def test_partial_remove_symptom_type_anonymous(anonymous_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    url_kwargs = {"symptom_type_uuid": symptom_type.uuid}
    url = reverse(REMOVE_SYMPTOM_PARTIAL_URL_NAME, kwargs=url_kwargs)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_partial_remove_symptom_type_authenticated_valid(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    entry = SymptomEntryFactory.create(user=user, symptom_type=symptom_type)

    url_kwargs = {"symptom_type_uuid": symptom_type.uuid}
    url = reverse(REMOVE_SYMPTOM_PARTIAL_URL_NAME, kwargs=url_kwargs)

    assert SymptomType.objects.filter(pk=symptom_type.pk).exists()
    assert SymptomEntry.objects.filter(pk=entry.pk).exists()

    # When
    response = authenticated_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.content == b""
    assert not SymptomType.objects.filter(pk=symptom_type.pk).exists()
    assert not SymptomEntry.objects.filter(pk=entry.pk).exists()


@pytest.mark.django_db
def test_partial_remove_symptom_type_not_found_returns_400(authenticated_client: Client) -> None:
    # Given
    invalid_uuid = uuid.uuid4()
    url_kwargs = {"symptom_type_uuid": invalid_uuid}
    url = reverse(REMOVE_SYMPTOM_PARTIAL_URL_NAME, kwargs=url_kwargs)

    # When
    response = authenticated_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid symptom type parameter provided." in response.content


@pytest.mark.django_db
def test_partial_remove_symptom_type_wrong_user_returns_400(
    authenticated_second_user_client: Client, user: User
) -> None:
    # Given
    symptom_type_user1 = SymptomTypeFactory.create(user=user)
    url_kwargs = {"symptom_type_uuid": symptom_type_user1.uuid}
    url = reverse(REMOVE_SYMPTOM_PARTIAL_URL_NAME, kwargs=url_kwargs)
    assert SymptomType.objects.filter(pk=symptom_type_user1.pk).exists()

    # When
    response = authenticated_second_user_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid symptom type parameter provided." in response.content
    assert SymptomType.objects.filter(pk=symptom_type_user1.pk).exists()


@pytest.mark.django_db
def test_partial_remove_symptom_type_get_not_allowed(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    url_kwargs = {"symptom_type_uuid": symptom_type.uuid}
    url = reverse(REMOVE_SYMPTOM_PARTIAL_URL_NAME, kwargs=url_kwargs)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_partial_remove_symptom_type_post_not_allowed(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    url_kwargs = {"symptom_type_uuid": symptom_type.uuid}
    url = reverse(REMOVE_SYMPTOM_PARTIAL_URL_NAME, kwargs=url_kwargs)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
