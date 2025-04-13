import uuid
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from allergy.models import Medication
from tests.factories.medication import MedicationFactory

DELETE_MEDICATION_PARTIAL_URL_NAME = "settings:partial_delete_medication"
LOGIN_URL_NAME = "login_view"
DASHBOARD_URL_NAME = "allergy:dashboard"


@pytest.mark.django_db
def test_partial_delete_medication_anonymous(anonymous_client: Client, user: User) -> None:
    # Given
    medication = MedicationFactory.create(user=user)
    url_kwargs = {"medication_uuid": medication.uuid}
    url = reverse(DELETE_MEDICATION_PARTIAL_URL_NAME, kwargs=url_kwargs)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_partial_delete_medication_authenticated_valid(authenticated_client: Client, user: User) -> None:
    # Given
    medication = MedicationFactory.create(user=user)
    url_kwargs = {"medication_uuid": medication.uuid}
    url = reverse(DELETE_MEDICATION_PARTIAL_URL_NAME, kwargs=url_kwargs)
    assert Medication.objects.filter(pk=medication.pk).exists()

    # When
    response = authenticated_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assert response.content == b""
    assert not Medication.objects.filter(pk=medication.pk).exists()


@pytest.mark.django_db
def test_partial_delete_medication_not_found_returns_400(authenticated_client: Client) -> None:
    # Given
    invalid_uuid = uuid.uuid4()
    url_kwargs = {"medication_uuid": invalid_uuid}
    url = reverse(DELETE_MEDICATION_PARTIAL_URL_NAME, kwargs=url_kwargs)

    # When
    response = authenticated_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid medication parameter provided." in response.content


@pytest.mark.django_db
def test_partial_delete_medication_wrong_user_returns_400(authenticated_second_user_client: Client, user: User) -> None:
    # Given
    medication_user1 = MedicationFactory.create(user=user)
    url_kwargs = {"medication_uuid": medication_user1.uuid}
    url = reverse(DELETE_MEDICATION_PARTIAL_URL_NAME, kwargs=url_kwargs)
    assert Medication.objects.filter(pk=medication_user1.pk).exists()

    # When
    response = authenticated_second_user_client.delete(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid medication parameter provided." in response.content
    assert Medication.objects.filter(pk=medication_user1.pk).exists()


@pytest.mark.django_db
def test_partial_delete_medication_get_not_allowed(authenticated_client: Client, user: User) -> None:
    # Given
    medication = MedicationFactory.create(user=user)
    url_kwargs = {"medication_uuid": medication.uuid}
    url = reverse(DELETE_MEDICATION_PARTIAL_URL_NAME, kwargs=url_kwargs)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_partial_delete_medication_post_not_allowed(authenticated_client: Client, user: User) -> None:
    # Given
    medication = MedicationFactory.create(user=user)
    url_kwargs = {"medication_uuid": medication.uuid}
    url = reverse(DELETE_MEDICATION_PARTIAL_URL_NAME, kwargs=url_kwargs)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
