from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects, assertTemplateUsed

from allergy.models import Medication
from tests.factories.medication import MedicationFactory

LIST_MEDICATIONS_PARTIAL_URL_NAME = "settings:partial_medication_list"
DELETE_MEDICATION_PARTIAL_URL_NAME = "settings:partial_delete_medication"
LOGIN_URL_NAME = "login_view"


@pytest.mark.django_db
def test_partial_medication_list_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(LIST_MEDICATIONS_PARTIAL_URL_NAME)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_partial_medication_list_no_medications(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(LIST_MEDICATIONS_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "settings/tabs/partials/medications/existing_medications.html")

    assert len(response.context["medications"]) == 0
    assertContains(response, "No medications added yet.")
    assertNotContains(response, '<li id="medication-item-')


@pytest.mark.django_db
def test_partial_medication_list_with_medications(authenticated_client: Client, user: User) -> None:
    # Given
    med1 = MedicationFactory.create(user=user, medication_name="Med 3", medication_type=Medication.MedicationType.PILLS)
    med2 = MedicationFactory.create(
        user=user, medication_name="Med 1", medication_type=Medication.MedicationType.INJECTION
    )
    med3 = MedicationFactory.create(
        user=user, medication_name="Med 2", medication_type=Medication.MedicationType.EYE_DROPS
    )

    url = reverse(LIST_MEDICATIONS_PARTIAL_URL_NAME)

    expected_delete_url_1_kwargs = {"medication_uuid": med1.uuid}
    expected_delete_url_2_kwargs = {"medication_uuid": med2.uuid}
    expected_delete_url_3_kwargs = {"medication_uuid": med3.uuid}

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/medications/existing_medications.html")

    medications_ctx = response.context["medications"]
    assert len(medications_ctx) == 3
    assert medications_ctx[0] == med2
    assert medications_ctx[1] == med3
    assert medications_ctx[2] == med1

    assertContains(response, f'<li id="medication-item-{med1.uuid}"')
    assertContains(response, med1.medication_name)
    assertContains(response, med1.get_medication_type_display())
    assertContains(response, reverse(DELETE_MEDICATION_PARTIAL_URL_NAME, kwargs=expected_delete_url_1_kwargs))

    assertContains(response, f'<li id="medication-item-{med2.uuid}"')
    assertContains(response, med2.medication_name)
    assertContains(response, med2.get_medication_type_display())
    assertContains(response, reverse(DELETE_MEDICATION_PARTIAL_URL_NAME, kwargs=expected_delete_url_2_kwargs))

    assertContains(response, f'<li id="medication-item-{med3.uuid}"')
    assertContains(response, med3.medication_name)
    assertContains(response, med3.get_medication_type_display())
    assertContains(response, reverse(DELETE_MEDICATION_PARTIAL_URL_NAME, kwargs=expected_delete_url_3_kwargs))

    assertContains(response, med1.icon_html)


@pytest.mark.django_db
def test_partial_medication_list_data_isolation(
    authenticated_client: Client, authenticated_second_user_client: Client, user: User, second_user: User
) -> None:
    # Given
    med_u1 = MedicationFactory.create(user=user, medication_name="User1 Med")
    med_u2 = MedicationFactory.create(user=second_user, medication_name="User2 Med")
    url = reverse(LIST_MEDICATIONS_PARTIAL_URL_NAME)

    # When
    response_user1 = authenticated_client.get(url)

    # Then
    assert response_user1.status_code == HTTPStatus.OK
    meds_u1 = response_user1.context["medications"]
    assert len(meds_u1) == 1
    assert meds_u1[0] == med_u1
    assertContains(response_user1, med_u1.medication_name)
    assertNotContains(response_user1, med_u2.medication_name)

    # When
    response_user2 = authenticated_second_user_client.get(url)

    # Then
    assert response_user2.status_code == HTTPStatus.OK
    meds_u2 = response_user2.context["medications"]
    assert len(meds_u2) == 1
    assert meds_u2[0] == med_u2
    assertNotContains(response_user2, med_u1.medication_name)
    assertContains(response_user2, med_u2.medication_name)


@pytest.mark.django_db
def test_partial_medication_list_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(LIST_MEDICATIONS_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
