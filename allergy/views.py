from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET
from django_htmx.http import trigger_client_event

from allergy.models import AllergiesEntry, AllergySymptoms


def redirect_to_dashboard(request: HttpRequest) -> HttpResponse:
    return redirect("dashboard")


def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "allergy/dashboard.html")


@require_GET
def get_calendar(request: HttpRequest, year: int, month: int, day: int) -> HttpResponse:
    allergies = AllergySymptoms.objects.filter(entry__user=request.user).all()

    response = render(request, "allergy/partials/allergy_symptoms.html", {"form": allergies})
    return trigger_client_event(response, name="allergy_symptoms_updated")
