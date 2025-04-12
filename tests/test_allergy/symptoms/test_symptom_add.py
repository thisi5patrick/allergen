import uuid
from datetime import date
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import NoReverseMatch, reverse
from pytest_django.asserts import assertContains, assertRedirects, assertTemplateUsed

from tests.factories.symptom_type import SymptomTypeFactory

SYMPTOM_ADD_URL = "allergy:symptom_add_partial"
LOGIN_URL_NAME = "login_view"
DASHBOARD_URL_NAME = "allergy:dashboard"


@pytest.mark.django_db
def test_symptom_add_anonymous(anonymous_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)

    expected_add_url_kwargs = {"symptom_uuid": symptom_type.uuid}
    url = reverse(SYMPTOM_ADD_URL, kwargs=expected_add_url_kwargs)

    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_symptom_add_authenticated_valid(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    test_date_str = "2024-05-21"
    expected_add_url_kwargs = {"symptom_uuid": symptom_type.uuid}
    url = reverse(SYMPTOM_ADD_URL, kwargs=expected_add_url_kwargs) + f"?selected_date={test_date_str}"

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK

    assertTemplateUsed(response, "allergy/partials/symptoms/intensity/add_selector.html")

    assert response.context["symptom_type"] == symptom_type
    assert response.context["selected_date_str"] == test_date_str
    assert response.context["selected_date"] == date.fromisoformat(test_date_str)

    assertContains(response, 'hx-swap-oob="true"')
    assertContains(response, f'id="symptom-{symptom_type.uuid}"')
    assertContains(response, "hx-delete=")


@pytest.mark.django_db
def test_symptom_add_authenticated_not_found_returns_400(authenticated_client: Client) -> None:
    # Given
    invalid_uuid = uuid.uuid4()
    test_date_str = "2024-05-21"
    expected_add_url_kwargs = {"symptom_uuid": invalid_uuid}
    url = reverse(SYMPTOM_ADD_URL, kwargs=expected_add_url_kwargs) + f"?selected_date={test_date_str}"

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid or unknown symptom specified." in response.content


@pytest.mark.django_db
def test_symptom_add_authenticated_wrong_user_returns_400(authenticated_second_user_client: Client, user: User) -> None:
    # Given
    symptom_type_other_user = SymptomTypeFactory.create(user=user)
    test_date_str = "2024-05-21"
    expected_add_url_kwargs = {"symptom_uuid": symptom_type_other_user.uuid}
    url = reverse(SYMPTOM_ADD_URL, kwargs=expected_add_url_kwargs) + f"?selected_date={test_date_str}"

    # When
    response = authenticated_second_user_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert b"Invalid or unknown symptom specified." in response.content


@pytest.mark.django_db
def test_symptom_add_missing_date_param_fails_template_render(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    expected_add_url_kwargs = {"symptom_uuid": symptom_type.uuid}
    url = reverse(SYMPTOM_ADD_URL, kwargs=expected_add_url_kwargs)

    # When / Then
    with pytest.raises(NoReverseMatch) as excinfo:
        authenticated_client.get(url)

    assert "symptom_remove_partial" in str(excinfo.value)
    assert "keyword arguments '{'year': '', 'month': '', 'day':" in str(excinfo.value)


@pytest.mark.django_db
def test_symptom_add_invalid_date_param_fails_template_render(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    test_date_str = "invalid-date-format"
    expected_add_url_kwargs = {"symptom_uuid": symptom_type.uuid}
    url = reverse(SYMPTOM_ADD_URL, kwargs=expected_add_url_kwargs) + f"?selected_date={test_date_str}"

    # When / Then
    with pytest.raises(NoReverseMatch) as excinfo:
        authenticated_client.get(url)

    assert "symptom_remove_partial" in str(excinfo.value)
    assert "keyword arguments '{'year': '', 'month': '', 'day':" in str(excinfo.value)


@pytest.mark.django_db
def test_symptom_add_post_not_allowed(authenticated_client: Client, user: User) -> None:
    # Given
    symptom_type = SymptomTypeFactory.create(user=user)
    expected_add_url_kwargs = {"symptom_uuid": symptom_type.uuid}
    url = reverse(SYMPTOM_ADD_URL, kwargs=expected_add_url_kwargs)

    # When
    response = authenticated_client.post(url)

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
