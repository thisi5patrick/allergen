from datetime import date
from http import HTTPStatus
from typing import cast

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from django_htmx.http import trigger_client_event

from allergy.forms import AddSymptomForm, DeleteSymptomForm
from allergy.models import AllergyEntry, SymptomType


def redirect_to_dashboard(request: HttpRequest) -> HttpResponse:
    return redirect("dashboard")


def dashboard(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)

    symptom_types = SymptomType.objects.filter(user=user).all()
    return render(request, "allergy/dashboard.html", {"symptom_types": symptom_types})


@require_GET
def get_calendar(request: HttpRequest, year: int, month: int, day: int) -> HttpResponse:
    selected_date = date(year, month, day)

    user = cast(User, request.user)
    entry = AllergyEntry.objects.filter(user=user, entry_date=selected_date).first()

    allergies = entry.symptom_records.all() if entry else []

    response = render(
        request, "allergy/partials/allergy_symptoms.html", {"allergies": allergies, "selected_date": selected_date}
    )
    return trigger_client_event(response, name="allergy_symptoms_updated")


@require_POST
def add_symptom(request: HttpRequest) -> HttpResponse:
    form = AddSymptomForm(request.POST, user=request.user)
    if not form.is_valid():
        return render(
            request,
            "allergy/partials/symptom_error.html",
            {
                "form": form,
            },
        )

    entry = form.save()
    selected_date = form.cleaned_data["date"]

    allergies = entry.symptom_records.all()

    response = render(
        request,
        "allergy/partials/allergy_symptoms.html",
        {
            "allergies": allergies,
            "selected_date": selected_date,
        },
    )
    return trigger_client_event(response, "allergy_symptoms_updated")


@require_POST
def delete_symptom(request: HttpRequest) -> HttpResponse:
    form = DeleteSymptomForm(request.POST, user=request.user)
    if not form.is_valid():
        return render(
            request,
            "allergy/partials/symptom_error.html",
            {
                "form": form,
            },
        )

    form.delete()

    return HttpResponse(status=HTTPStatus.NO_CONTENT)
