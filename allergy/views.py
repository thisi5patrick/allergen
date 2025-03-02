from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from django_htmx.http import trigger_client_event

from allergy.models import AllergiesEntry, AllergySymptoms
from datetime import date


def redirect_to_dashboard(request: HttpRequest) -> HttpResponse:
    return redirect("dashboard")


def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "allergy/dashboard.html")


@require_GET
def get_calendar(request: HttpRequest, year: int, month: int, day: int) -> HttpResponse:
    selected_date = date(year, month, day)

    entry = AllergiesEntry.objects.filter(user=request.user, date=selected_date).first()

    allergies = []
    if entry:
        allergies = entry.symptoms.all()

    response = render(
        request,
        "allergy/partials/allergy_symptoms.html",
        {
            "allergies": allergies,
            "selected_date": selected_date
        }
    )
    return trigger_client_event(response, name="allergy_symptoms_updated")


@require_POST
def add_symptom(request: HttpRequest) -> HttpResponse:
    date_ = request.POST.get("date")
    symptom = request.POST.get("symptom")
    intensity = int(request.POST.get("intensity", 1))

    entry, _ = AllergiesEntry.objects.get_or_create(
        user=request.user,
        date=date_
    )

    allergy_symptom, _ = AllergySymptoms.objects.update_or_create(
        entry=entry,
        symptom=symptom,
        defaults={"intensity": intensity}
    )

    allergies = entry.symptoms.all()

    response = render(
        request,
        "allergy/partials/allergy_symptoms.html",
        {
            "allergies": allergies,
            "selected_date": date_
        }
    )
    return trigger_client_event(response, "allergy_symptoms_updated")


@require_POST
def delete_symptom(request: HttpRequest) -> HttpResponse:
    date_ = request.POST.get("date")
    symptom = request.POST.get("symptom")

    entry = AllergiesEntry.objects.filter(
        user=request.user,
        date=date_
    ).first()

    if entry:
        deleted, _ = AllergySymptoms.objects.filter(
            entry=entry,
            symptom=symptom
        ).delete()

        if not entry.symptoms.exists():
            entry.delete()

    return JsonResponse({"success": True})
