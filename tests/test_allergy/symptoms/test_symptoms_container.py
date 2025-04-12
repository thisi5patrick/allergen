from datetime import date
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from parsel import Selector
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects, assertTemplateUsed

from tests.factories.symptom_entry import SymptomEntryFactory
from tests.factories.symptom_type import SymptomTypeFactory

SYMPTOMS_CONTAINER_URL = "allergy:symptoms_container_partial"
SYMPTOM_ADD_URL = "allergy:symptom_add_partial"
SYMPTOM_REMOVE_URL = "allergy:symptom_remove_partial"
LOGIN_URL_NAME = "login_view"
DASHBOARD_URL_NAME = "allergy:dashboard"


@pytest.mark.django_db
def test_symptoms_container_anonymous(anonymous_client: Client) -> None:
    # Given
    test_date = date(2024, 5, 20)
    url_kwargs = {
        "year": test_date.year,
        "month": test_date.month,
        "day": test_date.day,
    }
    url = reverse(SYMPTOMS_CONTAINER_URL, kwargs=url_kwargs)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_symptoms_container_authenticated(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type_1 = SymptomTypeFactory.create(user=user, name="Pollen")
    symptom_type_2 = SymptomTypeFactory.create(user=user, name="Dust Mites")
    entry_date = date(2024, 5, 20)
    entry_1 = SymptomEntryFactory.create(user=user, symptom_type=symptom_type_1, entry_date=entry_date, intensity=5)

    expected_container_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
    }
    url = reverse(SYMPTOMS_CONTAINER_URL, kwargs=expected_container_url_kwargs)

    expected_remove_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
        "symptom_uuid": symptom_type_1.uuid,
    }
    expected_remove_url = reverse(SYMPTOM_REMOVE_URL, kwargs=expected_remove_url_kwargs)

    expected_add_url_kwargs = {
        "symptom_uuid": symptom_type_2.uuid,
    }
    expected_add_url = reverse(SYMPTOM_ADD_URL, kwargs=expected_add_url_kwargs)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "allergy/partials/symptoms/symptoms_container.html")
    assertTemplateUsed(response, "allergy/partials/symptoms/symptoms_grid.html")
    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/existing_selectors.html")
    assertTemplateUsed(response, "allergy/partials/calendar/calendar_grid.html")

    context = response.context
    assert context["selected_date"] == entry_date
    assert context["selected_date_str"] == entry_date.strftime("%Y-%m-%d")

    symptom_types_in_context = context["symptom_types"]
    assert len(symptom_types_in_context) == 2
    assert set(symptom_types_in_context) == {symptom_type_1, symptom_type_2}

    symptom_entries_in_context = context["symptom_entries"]
    assert len(symptom_entries_in_context) == 1
    assert symptom_entries_in_context[0] == entry_1

    assert symptom_type_1 in context["selected_symptoms_map"]
    assert symptom_type_2 not in context["selected_symptoms_map"]
    assert context["selected_symptoms_map"][symptom_type_1] == entry_1
    assert "calendar_matrix" in context
    assert context["current_year"] == entry_date.year
    assert context["selected_day"] == entry_date.day
    assert "weekdays" in context

    assertContains(response, f'id="symptom-{symptom_type_1.uuid}"')
    assertContains(response, f'hx-delete="{expected_remove_url}"')
    assertContains(response, f'id="symptom-{symptom_type_2.uuid}"')
    assertContains(response, f'hx-get="{expected_add_url}"')
    assertContains(response, f'id="intensity-{symptom_type_1.uuid}"')
    selector = Selector(text=response.content.decode(response.charset))

    intensity_5_button = selector.xpath(f'//div[@id="intensity-{symptom_type_1.uuid}"]//button[normalize-space(.)="5"]')
    assert len(intensity_5_button) == 1

    button_classes = intensity_5_button.xpath("@class").get()
    assert button_classes is not None
    assert "bg-blue-500" in button_classes.split()


@pytest.mark.django_db
def test_symptoms_container_no_entries_for_date(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type_1 = SymptomTypeFactory.create(user=user, name="Pollen")
    symptom_type_2 = SymptomTypeFactory.create(user=user, name="Dust Mites")

    entry_date = date(2024, 5, 21)

    expected_container_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
    }
    url = reverse(SYMPTOMS_CONTAINER_URL, kwargs=expected_container_url_kwargs)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/symptoms/symptoms_container.html")

    context = response.context
    assert context["selected_date"] == entry_date

    symptom_types_in_context = context["symptom_types"]
    assert len(symptom_types_in_context) == 2
    assert set(symptom_types_in_context) == {symptom_type_1, symptom_type_2}

    symptom_entries_in_context = context["symptom_entries"]
    assert len(symptom_entries_in_context) == 0
    assert len(context["selected_symptoms_map"]) == 0

    assertContains(response, f'id="symptom-{symptom_type_1.uuid}"')
    assertContains(response, f'hx-get="{reverse(SYMPTOM_ADD_URL, kwargs={"symptom_uuid": symptom_type_1.uuid})}"')
    assertContains(response, f'id="symptom-{symptom_type_2.uuid}"')
    assertContains(response, f'hx-get="{reverse(SYMPTOM_ADD_URL, kwargs={"symptom_uuid": symptom_type_2.uuid})}"')
    assertContains(response, 'id="intensity-container"')

    selector = Selector(text=response.content.decode(response.charset))
    individual_intensity_selectors = selector.xpath(
        '//div[starts-with(@id, "intensity-") and @id!="intensity-container"]'
    )
    assert len(individual_intensity_selectors) == 0, "Found unexpected individual intensity selectors"


@pytest.mark.django_db
def test_symptoms_container_no_symptoms_defined(authenticated_client: Client, user: User) -> None:
    # Given
    entry_date = date(2024, 5, 21)

    expected_container_url_kwargs = {
        "year": entry_date.year,
        "month": entry_date.month,
        "day": entry_date.day,
    }
    url = reverse(SYMPTOMS_CONTAINER_URL, kwargs=expected_container_url_kwargs)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "allergy/partials/symptoms/symptoms_container.html")

    context = response.context
    assert context["selected_date"] == entry_date

    symptom_types_in_context = context["symptom_types"]
    assert len(symptom_types_in_context) == 0

    symptom_entries_in_context = context["symptom_entries"]
    assert len(symptom_entries_in_context) == 0
    assert len(context["selected_symptoms_map"]) == 0

    assertContains(response, '<div class="grid grid-cols-2')
    assertNotContains(response, '<button id="symptom-')


@pytest.mark.django_db
def test_symptoms_container_invalid_date(authenticated_client: Client) -> None:
    # Given
    url_kwargs = {"year": 2024, "month": 2, "day": 30}
    url = reverse(SYMPTOMS_CONTAINER_URL, kwargs=url_kwargs)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid date parameters provided." in response.content


@pytest.mark.django_db
def test_symptoms_container_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    url_kwargs = {"year": 2024, "month": 5, "day": 20}
    url = reverse(SYMPTOMS_CONTAINER_URL, kwargs=url_kwargs)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
