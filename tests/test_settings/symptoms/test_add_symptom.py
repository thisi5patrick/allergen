from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from allergy.models import SymptomType
from settings.forms.new_symptom import AddNewSymptomForm

NEW_SYMPTOM_FORM_PARTIAL_URL_NAME = "settings:partial_new_symptom_type_form"
SAVE_SYMPTOM_PARTIAL_URL_NAME = "settings:partial_new_symptom_type_save"
LOGIN_URL_NAME = "login_view"


@pytest.mark.django_db
def test_partial_new_symptom_form_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(NEW_SYMPTOM_FORM_PARTIAL_URL_NAME)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_partial_new_symptom_form_authenticated(authenticated_client: Client) -> None:
    # Given
    url = reverse(NEW_SYMPTOM_FORM_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/symptoms/add_symptom_type.html")
    assert "form" in response.context

    form = response.context["form"]
    assert isinstance(form, AddNewSymptomForm)
    assert not form.is_bound

    assertContains(response, "<form")
    assertContains(response, 'name="name"')
    assertContains(response, 'id="id_name"')
    assertContains(response, "Add Symptom")
    assertContains(response, "Only letters and spaces allowed")


@pytest.mark.django_db
def test_partial_new_symptom_form_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(NEW_SYMPTOM_FORM_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_partial_save_symptom_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(SAVE_SYMPTOM_PARTIAL_URL_NAME)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.post(url, {"name": "New Test"})

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_partial_save_symptom_authenticated_valid(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(SAVE_SYMPTOM_PARTIAL_URL_NAME)
    symptom_name = "Grass Pollen"
    post_data = {"name": symptom_name}
    assert not SymptomType.objects.filter(user=user, name=symptom_name).exists()

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/symptoms/add_symptom_type_oob.html")
    assert SymptomType.objects.filter(user=user, name=symptom_name).exists()

    new_symptom = SymptomType.objects.get(user=user, name=symptom_name)
    assert response.context["symptom_type"] == new_symptom
    assert isinstance(response.context["form"], AddNewSymptomForm)
    assert not response.context["form"].is_bound

    assertContains(response, 'hx-swap-oob="afterbegin"')
    assertContains(response, 'id="existing-symptoms-container"')
    assertContains(response, f'id="symptom-type-{new_symptom.uuid}"')
    assertContains(response, symptom_name)
    assertContains(response, "- 0 Entries")
    assertContains(response, "<form")
    assertContains(response, 'name="name"')


@pytest.mark.django_db
def test_partial_save_symptom_missing_name(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(SAVE_SYMPTOM_PARTIAL_URL_NAME)
    post_data = {"name": ""}

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/symptoms/add_symptom_type.html")

    form = response.context["form"]
    assert isinstance(form, AddNewSymptomForm)
    assert not form.is_valid()
    assert "name" in form.errors
    assert "This field is required." in form.errors["name"]
    assert response.context.get("symptom_type") is None
    assertContains(response, "This field is required.")


@pytest.mark.django_db
def test_partial_save_symptom_invalid_chars(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(SAVE_SYMPTOM_PARTIAL_URL_NAME)
    post_data = {"name": "Pollen!"}

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/symptoms/add_symptom_type.html")
    form = response.context["form"]
    assert isinstance(form, AddNewSymptomForm)
    assert not form.is_valid()
    assert "name" in form.errors
    assert "Symptom name should only contain letters and spaces" in form.errors["name"]
    assert response.context.get("symptom_type") is None
    assertContains(response, "Symptom name should only contain letters and spaces")


@pytest.mark.django_db
def test_partial_save_symptom_duplicate_name(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(SAVE_SYMPTOM_PARTIAL_URL_NAME)
    post_data = {"name": "existing symptom"}

    # When
    response = authenticated_client.post(url, post_data)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/partials/symptoms/add_symptom_type_oob.html")

    form = response.context["form"]
    assert isinstance(form, AddNewSymptomForm)
    assert not form.is_valid()
    assert "name" in form.errors
    assert "You already have a symptom with this name." in form.errors["name"]
    assert response.context.get("symptom_type") is None
    assertContains(response, "You already have a symptom with this name.")
    assert SymptomType.objects.filter(user=user, name__iexact="Existing Symptom").count() == 1


@pytest.mark.django_db
def test_partial_save_symptom_get_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(SAVE_SYMPTOM_PARTIAL_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
