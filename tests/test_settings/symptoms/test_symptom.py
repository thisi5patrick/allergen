from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from settings.views.enums import ActiveTab

SETTINGS_SYMPTOMS_URL_NAME = "settings:symptoms_tab"
EXISTING_SYMPTOMS_PARTIAL_URL_NAME = "settings:partial_existing_symptoms"
NEW_SYMPTOM_FORM_PARTIAL_URL_NAME = "settings:partial_new_symptom_type_form"
LOGIN_URL_NAME = "login_view"


@pytest.mark.django_db
def test_symptoms_tab_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(SETTINGS_SYMPTOMS_URL_NAME)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_symptoms_tab_authenticated(authenticated_client: Client) -> None:
    # Given
    url = reverse(SETTINGS_SYMPTOMS_URL_NAME)
    expected_form_url = reverse(NEW_SYMPTOM_FORM_PARTIAL_URL_NAME)
    expected_list_url = reverse(EXISTING_SYMPTOMS_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/symptoms.html")
    assertTemplateUsed(response, "settings/base.html")

    assert response.context["active_tab"] == ActiveTab.SYMPTOMS
    assertContains(response, f'hx-get="{expected_form_url}"')
    assertContains(response, 'id="add-symptom-form-container"')
    assertContains(response, f'hx-get="{expected_list_url}"')
    assertContains(response, 'id="existing-symptoms-container"')


@pytest.mark.django_db
def test_symptoms_tab_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(SETTINGS_SYMPTOMS_URL_NAME)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
