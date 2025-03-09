from django.db.models import Case, CharField, Count, Value, When
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from allergy.models import AllergyEntries, AllergySymptoms


@require_GET
def user_overview(request: HttpRequest) -> HttpResponse:
    days_with_symptoms = (
        AllergyEntries.objects.filter(user_id=request.user.id).annotate(count=Count("entry_date")).count()
    )
    total_entries = AllergySymptoms.objects.filter(entry__user_id=request.user.id).count()
    recent_symptoms = AllergySymptoms.objects.filter(entry__user_id=request.user.id).order_by("-created_at").all()[:5]
    top_symptoms = None  # TODO: add top symptoms
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
