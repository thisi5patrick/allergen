import uuid
from datetime import date
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from parsel import Selector
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from allergy.forms import AddSymptomForm
from allergy.models import SymptomEntry
from tests.factories.symptom_entry import SymptomEntryFactory
from tests.factories.symptom_type import SymptomTypeFactory

SYMPTOM_SAVE_URL = "allergy:symptom_save_partial"
LOGIN_URL_NAME = "login_view"


@pytest.mark.django_db()
def test_symptom_save_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(SYMPTOM_SAVE_URL)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.post(url, {})

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db()
def test_symptom_save_authenticated_create_valid(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    url = reverse(SYMPTOM_SAVE_URL)
    entry_date = date(2024, 5, 22)
    intensity = 7
    post_data = {
        "symptom_uuid": str(symptom_type.uuid),
        "intensity": intensity,
        "selected_date": entry_date.strftime("%Y-%m-%d"),
    }
    assert not SymptomEntry.objects.filter(user=user, entry_date=entry_date, symptom_type=symptom_type).exists()

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/select_intensity.html")
    assert "entry" in response.context
    new_entry = response.context["entry"]
    assert isinstance(new_entry, SymptomEntry)
    assert new_entry.symptom_type == symptom_type
    assert new_entry.intensity == intensity
    assert new_entry.entry_date == entry_date
    assert new_entry.user == user
    assert response.context["symptom_type"] == symptom_type
    db_entry = SymptomEntry.objects.get(user=user, entry_date=entry_date, symptom_type=symptom_type)
    assert db_entry.intensity == intensity
    selector = Selector(text=response.content.decode(response.charset))
    intensity_button = selector.xpath(f'//button[normalize-space(.)="{intensity}"]')
    button_classes_str = intensity_button.xpath("@class").get()
    assert button_classes_str is not None
    assert "bg-blue-500" in button_classes_str.split()


@pytest.mark.django_db()
def test_symptom_save_authenticated_update_valid(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    entry_date = date(2024, 5, 20)
    entry = SymptomEntryFactory.create(user=user, symptom_type=symptom_type, entry_date=entry_date, intensity=5)
    url = reverse(SYMPTOM_SAVE_URL)
    new_intensity = 9
    post_data = {
        "symptom_uuid": str(symptom_type.uuid),
        "intensity": new_intensity,
        "selected_date": entry_date.strftime("%Y-%m-%d"),
    }
    original_pk = entry.pk

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/select_intensity.html")
    assert "entry" in response.context
    updated_entry = response.context["entry"]
    assert updated_entry.pk == original_pk
    assert updated_entry.intensity == new_intensity
    assert updated_entry.symptom_type == symptom_type
    assert updated_entry.entry_date == entry_date
    db_entry = SymptomEntry.objects.get(pk=original_pk)
    assert db_entry.intensity == new_intensity
    selector = Selector(text=response.content.decode(response.charset))
    intensity_button = selector.xpath(f'//button[normalize-space(.)="{new_intensity}"]')
    button_classes_str = intensity_button.xpath("@class").get()
    assert button_classes_str is not None
    assert "bg-blue-500" in button_classes_str.split()


@pytest.mark.django_db()
@pytest.mark.parametrize(
    ("field_to_miss", "expected_error_part"),
    [
        ("symptom_uuid", "This field is required."),
        ("intensity", "This field is required."),
        ("selected_date", "This field is required."),
    ],
)
def test_symptom_save_missing_data(
    authenticated_client: Client, user: User, field_to_miss: str, expected_error_part: str
) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    url = reverse(SYMPTOM_SAVE_URL)
    valid_data = {
        "symptom_uuid": str(symptom_type.uuid),
        "intensity": 5,
        "selected_date": "2024-05-23",
    }
    post_data = valid_data.copy()
    del post_data[field_to_miss]

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/select_intensity.html")
    assert "form" in response.context
    form = response.context["form"]
    assert isinstance(form, AddSymptomForm)
    assert not form.is_valid()
    assert field_to_miss in form.errors
    assert any(expected_error_part in e for e in form.errors[field_to_miss])
    if field_to_miss != "symptom_uuid":
        assert response.context["symptom_type"] == symptom_type
    else:
        assert response.context["symptom_type"] is None
    assertContains(response, expected_error_part)


@pytest.mark.django_db()
@pytest.mark.parametrize("intensity_value", [1, 10])
def test_symptom_save_boundary_intensity(authenticated_client: Client, user: User, intensity_value: int) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    url = reverse(SYMPTOM_SAVE_URL)
    entry_date = date(2024, 5, 22)
    post_data = {
        "symptom_uuid": str(symptom_type.uuid),
        "intensity": intensity_value,
        "selected_date": entry_date.strftime("%Y-%m-%d"),
    }

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/select_intensity.html")
    assert "entry" in response.context
    new_entry = response.context["entry"]
    assert new_entry.intensity == intensity_value
    db_entry = SymptomEntry.objects.get(user=user, entry_date=entry_date, symptom_type=symptom_type)
    assert db_entry.intensity == intensity_value


@pytest.mark.django_db()
@pytest.mark.parametrize("invalid_intensity", [0, 11, "abc"])
def test_symptom_save_invalid_intensity(authenticated_client: Client, user: User, invalid_intensity: str | int) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    url = reverse(SYMPTOM_SAVE_URL)
    post_data = {
        "symptom_uuid": str(symptom_type.uuid),
        "intensity": invalid_intensity,
        "selected_date": "2024-05-23",
    }

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/select_intensity.html")
    assert "form" in response.context
    form = response.context["form"]
    assert isinstance(form, AddSymptomForm)
    assert not form.is_valid()
    assert "intensity" in form.errors
    if isinstance(invalid_intensity, str):
        assert "Enter a whole number." in form.errors["intensity"]
    else:
        assert "Ensure this value is" in form.errors["intensity"][0]
    assert response.context["symptom_type"] == symptom_type
    assertContains(response, "intensity")


@pytest.mark.django_db()
def test_symptom_save_invalid_date_format(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    url = reverse(SYMPTOM_SAVE_URL)
    post_data = {
        "symptom_uuid": str(symptom_type.uuid),
        "intensity": 5,
        "selected_date": "not-a-date",  # Invalid format
    }

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/select_intensity.html")
    assert "form" in response.context
    form = response.context["form"]
    assert isinstance(form, AddSymptomForm)
    assert not form.is_valid()
    assert "selected_date" in form.errors
    assert "Enter a valid date." in form.errors["selected_date"]
    assert response.context["symptom_type"] == symptom_type
    assertContains(response, "Enter a valid date")


@pytest.mark.django_db()
def test_symptom_save_invalid_symptom_uuid_format_or_nonexistent(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(SYMPTOM_SAVE_URL)
    invalid_uuid = uuid.uuid4()
    post_data_nonexistent = {
        "symptom_uuid": str(invalid_uuid),
        "intensity": 5,
        "selected_date": "2024-05-23",
    }
    post_data_garbage = {
        "symptom_uuid": "not-a-uuid",
        "intensity": 5,
        "selected_date": "2024-05-23",
    }

    # When
    response_nonexistent = authenticated_client.post(url, post_data_nonexistent)

    # Then
    assert response_nonexistent.status_code == HTTPStatus.OK
    assert "form" in response_nonexistent.context
    form_nonexistent = response_nonexistent.context["form"]
    assert isinstance(form_nonexistent, AddSymptomForm)
    assert not form_nonexistent.is_valid()
    assert "symptom_uuid" in form_nonexistent.errors
    assert "Invalid symptom type" in form_nonexistent.errors["symptom_uuid"]
    assert response_nonexistent.context["symptom_type"] is None

    # When
    response_garbage = authenticated_client.post(url, post_data_garbage)

    # Then
    assert response_garbage.status_code == HTTPStatus.OK
    assert "form" in response_garbage.context
    form_garbage = response_garbage.context["form"]
    assert isinstance(form_garbage, AddSymptomForm)
    assert not form_garbage.is_valid()
    assert "symptom_uuid" in form_garbage.errors
    assert "Enter a valid UUID." in form_garbage.errors["symptom_uuid"]
    assert response_garbage.context["symptom_type"] is None


@pytest.mark.django_db()
def test_symptom_save_wrong_user_symptom_uuid(authenticated_second_user_client: Client, user: User) -> None:
    # Given
    symptom_type_user1 = SymptomTypeFactory.create(user=user)
    url = reverse(SYMPTOM_SAVE_URL)
    post_data = {
        "symptom_uuid": str(symptom_type_user1.uuid),
        "intensity": 5,
        "selected_date": "2024-05-23",
    }

    # When
    response = authenticated_second_user_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assert "form" in response.context
    form = response.context["form"]
    assert isinstance(form, AddSymptomForm)
    assert not form.is_valid()
    assert "symptom_uuid" in form.errors
    assert "Invalid symptom type" in form.errors["symptom_uuid"]
    assert response.context["symptom_type"] is None


@pytest.mark.django_db()
def test_symptom_save_get_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(SYMPTOM_SAVE_URL)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
