from typing import cast

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from allergy.models import SymptomEntry


@require_GET
def overview_view(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)

    entries = SymptomEntry.objects.filter(user=user)

    days_with_symptoms = entries.values("entry_date").distinct().count()
    total_entries = entries.count()
    recent_symptoms = entries.select_related("symptom_type").order_by("-created_at")[:5]
    top_symptoms = (
        entries.values("symptom_type__name").annotate(count=Count("symptom_type__name")).order_by("-count")[:5]
    )

    context = {
        "days_with_symptoms": days_with_symptoms,
        "total_entries": total_entries,
        "recent_symptoms": recent_symptoms,
        "top_symptoms": top_symptoms,
    }
    return render(request, "user/tabs/user_overview.html", context)


@require_GET
def symptoms_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_symptoms.html", {"active_tab": "symptoms"})


@require_GET
def food_allergies_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": "food_allergies"})


@require_GET
def medications_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": "medications"})


@require_GET
def change_password_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": "change_password"})


@require_GET
def delete_account_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": "delete_account"})
