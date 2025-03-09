from datetime import date
from typing import cast

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from django_htmx.http import trigger_client_event

from allergy.models import AllergyEntries, AllergySymptoms


def redirect_to_dashboard(request: HttpRequest) -> HttpResponse:
    return redirect("dashboard")


def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "allergy/dashboard.html")


@require_GET
def get_calendar(request: HttpRequest, year: int, month: int, day: int) -> HttpResponse:
    selected_date = date(year, month, day)

    user = cast(User, request.user)
    entry = AllergyEntries.objects.filter(user=user, entry_date=selected_date).first()

    allergies = entry.symptoms.all() if entry else []

    response = render(
        request, "allergy/partials/allergy_symptoms.html", {"allergies": allergies, "selected_date": selected_date}
    )
    return trigger_client_event(response, name="allergy_symptoms_updated")


@require_POST
def add_symptom(request: HttpRequest) -> HttpResponse:
    date_ = request.POST.get("date")
    symptom = request.POST.get("symptom")
    intensity = int(request.POST.get("intensity", 1))

    entry, _ = AllergyEntries.objects.get_or_create(user=request.user, entry_date=date_)

    allergy_symptom, _ = AllergySymptoms.objects.update_or_create(
        entry=entry, symptom=symptom, defaults={"intensity": intensity}
    )

    allergies = entry.symptoms.all()

    response = render(
        request, "allergy/partials/allergy_symptoms.html", {"allergies": allergies, "selected_date": date_}
    )
    return trigger_client_event(response, "allergy_symptoms_updated")


@require_POST
def delete_symptom(request: HttpRequest) -> HttpResponse:
    symptom_date_str = request.POST.get("date")
    symptom = request.POST.get("symptom")

    if not symptom_date_str or not symptom:
        return JsonResponse({"success": False, "error": "Invalid data provided."})

    symptom_date = date.fromisoformat(symptom_date_str)

    user = cast(User, request.user)
    entry = AllergyEntries.objects.filter(user=user, entry_date=symptom_date).first()

    if entry:
        deleted, _ = AllergySymptoms.objects.filter(entry=entry, symptom=symptom).delete()

        if not entry.symptoms.exists():
            entry.delete()

    return JsonResponse({"success": True})
