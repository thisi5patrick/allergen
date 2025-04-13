from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from settings.views.enums import ActiveTab

SETTINGS_MEDICATIONS_URL_NAME = "settings:medications_tab"
LIST_MEDICATIONS_PARTIAL_URL_NAME = "settings:partial_medication_list"
NEW_MEDICATION_FORM_PARTIAL_URL_NAME = "settings:partial_new_medication_form"
LOGIN_URL_NAME = "login_view"


@pytest.mark.django_db
def test_medications_tab_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(SETTINGS_MEDICATIONS_URL_NAME)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_medications_tab_authenticated(authenticated_client: Client) -> None:
    # Given
    url = reverse(SETTINGS_MEDICATIONS_URL_NAME)
    expected_form_url = reverse(NEW_MEDICATION_FORM_PARTIAL_URL_NAME)
    expected_list_url = reverse(LIST_MEDICATIONS_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/medications.html")
    assertTemplateUsed(response, "settings/base.html")

    assert response.context["active_tab"] == ActiveTab.MEDICATIONS

    assertContains(response, f'hx-get="{expected_form_url}"')
    assertContains(response, 'id="medication-form-container"')
    assertContains(response, f'hx-get="{expected_list_url}"')
    assertContains(response, 'id="medication-list-container"')


@pytest.mark.django_db
def test_medications_tab_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(SETTINGS_MEDICATIONS_URL_NAME)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
