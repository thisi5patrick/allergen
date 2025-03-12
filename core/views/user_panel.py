from typing import cast

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from allergy.models import AllergyEntry, SymptomRecord


@require_GET
def user_overview(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)

    entries = AllergyEntry.objects.filter(user=user)
    records = SymptomRecord.objects.filter(entry__user=user)

    days_with_symptoms = entries.filter(symptom_records__isnull=False).values("entry_date").distinct().count()
    total_entries = records.count()
    recent_symptoms = records.select_related("symptom_type", "entry").order_by("-created_at")[:5]
    top_symptoms = (
        records.values("symptom_type__name").annotate(count=Count("symptom_type__name")).order_by("-count")[:5]
    )

    context = {
        "days_with_symptoms": days_with_symptoms,
        "total_entries": total_entries,
        "recent_symptoms": recent_symptoms,
        "top_symptoms": top_symptoms,
    }
    return render(request, "user/tabs/user_overview.html", context)


@require_GET
def user_symptoms(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_symptoms.html", {"active_tab": "symptoms"})


@require_GET
def user_food_allergies(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": "food_allergies"})


@require_GET
def user_medications(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": "medications"})


@require_GET
def change_password(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": "change_password"})


@require_GET
def delete_account(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": "delete_account"})
