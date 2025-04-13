from datetime import timedelta
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects, assertTemplateUsed

from settings.views.enums import ActiveTab
from tests.factories.symptom_entry import SymptomEntryFactory
from tests.factories.symptom_type import SymptomTypeFactory

OVERVIEW_TAB_URL_NAME = "settings:overview_tab"
LOGIN_URL_NAME = "login_view"


@pytest.mark.django_db
def test_overview_tab_anonymous(anonymous_client: Client) -> None:
    # Given
    url = reverse(OVERVIEW_TAB_URL_NAME)
    expected_redirect_url = reverse(LOGIN_URL_NAME)

    # When
    response = anonymous_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, expected_redirect_url)


@pytest.mark.django_db
def test_overview_tab_authenticated_no_data(authenticated_client: Client, user: User) -> None:
    # Given
    url = reverse(OVERVIEW_TAB_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/overview.html")
    assertTemplateUsed(response, "settings/base.html")

    context = response.context
    assert context["active_tab"] == ActiveTab.OVERVIEW
    assert context["days_with_symptoms"] == 0
    assert context["total_entries"] == 0
    assert len(context["recent_symptoms"]) == 0
    assert len(context["top_symptoms"]) == 0

    assertContains(response, "Days with recorded symptoms")
    assertContains(response, '<h3 class="text-lg font-semibold text-gray-800">0</h3>')
    assertContains(response, "No recent symptom entries.")
    assertContains(response, "Start tracking your symptoms to see a summary.")
    assertContains(response, user.username)


@pytest.mark.django_db
def test_overview_tab_authenticated_with_data(authenticated_client: Client, user: User) -> None:
    # Given
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    type_pollen = SymptomTypeFactory.create(user=user, name="Pollen")
    type_dust = SymptomTypeFactory.create(user=user, name="Dust Mites")
    type_cat = SymptomTypeFactory.create(user=user, name="Cat Dander")

    entry1_pollen_yest = SymptomEntryFactory.create(
        user=user, symptom_type=type_pollen, entry_date=yesterday, intensity=5
    )
    entry2_dust_yest = SymptomEntryFactory.create(user=user, symptom_type=type_dust, entry_date=yesterday, intensity=7)
    entry3_pollen_2days = SymptomEntryFactory.create(
        user=user, symptom_type=type_pollen, entry_date=two_days_ago, intensity=6
    )
    entry4_cat_today = SymptomEntryFactory.create(user=user, symptom_type=type_cat, entry_date=today, intensity=8)
    entry5_pollen_today = SymptomEntryFactory.create(user=user, symptom_type=type_pollen, entry_date=today, intensity=4)

    url = reverse(OVERVIEW_TAB_URL_NAME)

    # When
    response = authenticated_client.get(url)

    # Then
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, "settings/tabs/overview.html")

    context = response.context
    assert context["active_tab"] == ActiveTab.OVERVIEW
    assert context["days_with_symptoms"] == 3
    assert context["total_entries"] == 5

    recent_symptoms = context["recent_symptoms"]
    assert len(recent_symptoms) == 5
    assert recent_symptoms[0] in [entry4_cat_today, entry5_pollen_today]
    assert recent_symptoms[1] in [entry4_cat_today, entry5_pollen_today]
    assert entry1_pollen_yest in recent_symptoms
    assert entry2_dust_yest in recent_symptoms
    assert entry3_pollen_2days in recent_symptoms

    top_symptoms = context["top_symptoms"]
    assert len(top_symptoms) == 3
    assert top_symptoms[0]["symptom_type__name"] == "Pollen"
    assert top_symptoms[0]["count"] == 3
    top_names_counts = {(item["symptom_type__name"], item["count"]) for item in top_symptoms}
    assert ("Dust Mites", 1) in top_names_counts
    assert ("Cat Dander", 1) in top_names_counts

    assertContains(response, '<h3 class="text-lg font-semibold text-gray-800">3</h3>')
    assertContains(response, '<h3 class="text-lg font-semibold text-gray-800">5</h3>')
    assertContains(response, "Recent Activity")
    assertContains(response, f"{type_cat.name} (Intensity: {entry4_cat_today.intensity})")
    assertContains(response, f"{type_pollen.name} (Intensity: {entry5_pollen_today.intensity})")
    assertContains(response, "Allergy Summary")
    assertContains(response, f"{type_pollen.name} (3)")
    assertContains(response, f"{type_dust.name} (1)")
    assertContains(response, f"{type_cat.name} (1)")


@pytest.mark.django_db
def test_overview_tab_data_isolation(
    authenticated_client: Client, authenticated_second_user_client: Client, user: User, second_user: User
) -> None:
    # Given
    today = timezone.now().date()
    type_pollen_u1 = SymptomTypeFactory.create(user=user, name="Pollen")
    type_cat_u2 = SymptomTypeFactory.create(user=second_user, name="Cat")

    entry_u1_1 = SymptomEntryFactory.create(user=user, symptom_type=type_pollen_u1, entry_date=today, intensity=5)
    entry_u1_2 = SymptomEntryFactory.create(
        user=user, symptom_type=type_pollen_u1, entry_date=today - timedelta(days=1), intensity=6
    )

    entry_u2_1 = SymptomEntryFactory.create(user=second_user, symptom_type=type_cat_u2, entry_date=today, intensity=8)

    url = reverse(OVERVIEW_TAB_URL_NAME)

    # When
    response_user1 = authenticated_client.get(url)

    # Then
    assert response_user1.status_code == HTTPStatus.OK
    context_user1 = response_user1.context
    assert context_user1["days_with_symptoms"] == 2
    assert context_user1["total_entries"] == 2
    assert len(context_user1["recent_symptoms"]) == 2
    assert entry_u1_1 in context_user1["recent_symptoms"]
    assert entry_u1_2 in context_user1["recent_symptoms"]
    assert len(context_user1["top_symptoms"]) == 1
    assert context_user1["top_symptoms"][0]["symptom_type__name"] == "Pollen"
    assert context_user1["top_symptoms"][0]["count"] == 2
    assertContains(response_user1, user.username)
    assertNotContains(response_user1, second_user.username)
    assertNotContains(response_user1, type_cat_u2.name)

    response_user2 = authenticated_second_user_client.get(url)

    assert response_user2.status_code == HTTPStatus.OK
    context_user2 = response_user2.context
    assert context_user2["days_with_symptoms"] == 1
    assert context_user2["total_entries"] == 1
    assert len(context_user2["recent_symptoms"]) == 1
    assert context_user2["recent_symptoms"][0] == entry_u2_1
    assert len(context_user2["top_symptoms"]) == 1
    assert context_user2["top_symptoms"][0]["symptom_type__name"] == "Cat"
    assert context_user2["top_symptoms"][0]["count"] == 1
    assertContains(response_user2, second_user.username)
    assertNotContains(response_user2, user.username)
    assertNotContains(response_user2, type_pollen_u1.name)


@pytest.mark.django_db
def test_overview_tab_post_not_allowed(authenticated_client: Client) -> None:
    # Given
    url = reverse(OVERVIEW_TAB_URL_NAME)

    # When
    response = authenticated_client.post(url, {})

    # Then
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
