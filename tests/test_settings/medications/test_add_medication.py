from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from allergy.forms import MedicationForm
from allergy.models import Medication
from tests.factories.medication import MedicationFactory

NEW_MEDICATION_FORM_PARTIAL_URL_NAME = "settings:partial_new_medication_form"
SAVE_MEDICATION_PARTIAL_URL_NAME = "settings:partial_add_medication"
LOGIN_URL_NAME = "login_view"


@pytest.mark.django_db
def test_partial_new_medication_form_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(NEW_MEDICATION_FORM_PARTIAL_URL_NAME)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_partial_new_medication_form_authenticated(authenticated_client: Client) -> None:
    # Given
    url = reverse(NEW_MEDICATION_FORM_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/medications/add_medication_form.html")
    assert "form" in response.context
    form = response.context["form"]
    assert isinstance(form, MedicationForm)
    assert not form.is_bound
    assertContains(response, "<form")
    assertContains(response, 'name="medication_name"')
    assertContains(response, 'id="id_medication_name"')
    assertContains(response, 'name="medication_type"')
    assertContains(response, 'id="id_medication_type"')
    assertContains(response, "Add Medication")


@pytest.mark.django_db
def test_partial_new_medication_form_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(NEW_MEDICATION_FORM_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_partial_save_medication_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(SAVE_MEDICATION_PARTIAL_URL_NAME)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.post(url, {"medication_name": "Test", "medication_type": "pills"})

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_partial_save_medication_authenticated_valid(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(SAVE_MEDICATION_PARTIAL_URL_NAME)
    med_name = "Claritin"
    med_type = Medication.MedicationType.PILLS
    post_data = {"medication_name": med_name, "medication_type": med_type}
    assert not Medication.objects.filter(user=user, medication_name=med_name, medication_type=med_type).exists()

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/medications/add_medication.html")
    assert Medication.objects.filter(user=user, medication_name=med_name, medication_type=med_type).exists()
    new_med = Medication.objects.get(user=user, medication_name=med_name, medication_type=med_type)
    assert response.context["medication"] == new_med
    assert isinstance(response.context["form"], MedicationForm)
    assert not response.context["form"].is_bound

    assertContains(response, 'hx-swap-oob="afterbegin"')
    assertContains(response, 'id="medication-list-ul"')
    assertContains(response, f'<li id="medication-item-{new_med.uuid}"')
    assertContains(response, med_name)
    assertContains(response, new_med.get_medication_type_display())
    assertContains(response, new_med.icon_html)
    assertContains(response, 'id="no-medications-message" hx-swap-oob="delete"')
    assertContains(response, "<form")
    assertContains(response, 'name="medication_name"')


@pytest.mark.django_db
@pytest.mark.parametrize("field_to_miss", ["medication_name", "medication_type"])
def test_partial_save_medication_missing_data(authenticated_client: Client, user: User, field_to_miss: str) -> None:
    # Given
    url = reverse(SAVE_MEDICATION_PARTIAL_URL_NAME)
    valid_data = {
        "medication_name": "Benadryl",
        "medication_type": Medication.MedicationType.PILLS,
    }
    post_data = valid_data.copy()
    del post_data[field_to_miss]

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/medications/add_medication_form.html")
    assert "form" in response.context
    form = response.context["form"]
    assert isinstance(form, MedicationForm)
    assert not form.is_valid()
    assert field_to_miss in form.errors
    assert "This field is required." in form.errors[field_to_miss]
    assertContains(response, "This field is required.")


@pytest.mark.django_db
def test_partial_save_medication_duplicate(authenticated_client: Client, user: User) -> None:
    # Given
    med_name = "Flonase"
    med_type = Medication.MedicationType.NOSE_DROPS
    MedicationFactory.create(user=user, medication_name=med_name, medication_type=med_type)
    url = reverse(SAVE_MEDICATION_PARTIAL_URL_NAME)
    post_data = {"medication_name": med_name, "medication_type": med_type}

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/medications/add_medication_form.html")
    form = response.context["form"]
    assert isinstance(form, MedicationForm)
    assert not form.is_valid()
    expected_error_msg = "This medication with the same type already exists for you."
    assert expected_error_msg in form.non_field_errors() or (
        "medication_name" in form.errors and expected_error_msg in form.errors["medication_name"]
    )
    assertContains(response, expected_error_msg)
    assert Medication.objects.filter(user=user, medication_name=med_name, medication_type=med_type).count() == 1


@pytest.mark.django_db
def test_partial_save_medication_invalid_type(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(SAVE_MEDICATION_PARTIAL_URL_NAME)
    post_data = {"medication_name": "Aspirin", "medication_type": "invalid_choice"}

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/medications/add_medication_form.html")
    form = response.context["form"]
    assert isinstance(form, MedicationForm)
    assert not form.is_valid()
    assert "medication_type" in form.errors
    assert "Select a valid choice." in form.errors["medication_type"][0]
    assertContains(response, "Select a valid choice.")


@pytest.mark.django_db
def test_partial_save_medication_get_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(SAVE_MEDICATION_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
