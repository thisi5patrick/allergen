from datetime import date, timedelta
from http import HTTPStatus

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from pytest_django import DjangoAssertNumQueries

from tests.factories.symptom_entry import SymptomEntryFactory
from tests.factories.symptom_type import SymptomTypeFactory


@pytest.mark.django_db()
def test_overview_view(authenticated_client: Client, user: User) -> None:
    # GIVEN
    endpoint = reverse("overview_view")

    today = date.today()
    yesterday = date.today() - timedelta(days=1)

    symptom_type_1 = SymptomTypeFactory.create(user=user, name="test_symptom_1")
    symptom_type_2 = SymptomTypeFactory.create(user=user, name="test_symptom_2")

    SymptomEntryFactory.create(entry_date=today, symptom_type=symptom_type_1, user=user)
    SymptomEntryFactory.create(entry_date=yesterday, symptom_type=symptom_type_1, user=user)
    SymptomEntryFactory.create(entry_date=today, symptom_type=symptom_type_2, user=user)

    # WHEN
    response = authenticated_client.get(endpoint)

    # THEN
    assert response.status_code == HTTPStatus.OK

    assert response.context["days_with_symptoms"] == 2
    assert response.context["total_entries"] == 3
    assert len(response.context["recent_symptoms"]) == 3
    assert len(response.context["top_symptoms"]) == 2


@pytest.mark.django_db()
@pytest.mark.parametrize("number_of_symptoms", [2, 10, 50, 500])
def test_overview_view_with_consistent_query_numbers(
    number_of_symptoms: int, authenticated_client: Client, django_assert_num_queries: DjangoAssertNumQueries, user: User
) -> None:
    # GIVEN
    endpoint = reverse("overview_view")

    SymptomEntryFactory.create_batch(number_of_symptoms, user=user, symptom_type__user=user)

    # WHEN/THEN
    with django_assert_num_queries(6):
        authenticated_client.get(endpoint)
