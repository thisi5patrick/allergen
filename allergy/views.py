import calendar
from datetime import date
from http import HTTPStatus
from typing import cast

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from allergy.forms import AddSymptomForm, DeleteSymptomForm
from allergy.models import SymptomEntry, SymptomType


def redirect_to_dashboard(request: HttpRequest) -> HttpResponse:
    return redirect("dashboard")


@require_GET
def dashboard(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)

    symptom_types = SymptomType.objects.filter(user=user).all()
    today = date.today()
    context = {
        "symptom_types": symptom_types,
        "current_year": today.year,
        "current_month": today.month,
        "current_day": today.day,
    }
    return render(request, "allergy/dashboard.html", context)


@require_GET
def partial_calendar(request: HttpRequest, year: int, month: int, day: int | None = None) -> HttpResponse:
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    selected_day = day
    if day:
        selected_date = date(year, month, day).strftime("%Y-%m-%d")
    else:
        selected_date = None

    context = {
        "calendar": cal,
        "month": month,
        "month_name": month_name,
        "year": year,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "selected_day": selected_day,
        "selected_date": selected_date,
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    }

    return render(request, "allergy/partials/calendar/calendar.html", context)


@require_GET
def partial_symptoms_container(request: HttpRequest, year: int, month: int, day: int) -> HttpResponse:
    selected_date = date(year, month, day)
    user = cast(User, request.user)

    symptom_entries = SymptomEntry.objects.filter(user=user).filter(entry_date=selected_date).all()
    all_symptom_types = SymptomType.objects.filter(user=user).all()
    selected_symptoms = {entry.symptom_type: entry for entry in symptom_entries}

    cal = calendar.monthcalendar(year, month)
    selected_day = day

    context = {
        "symptom_entries": symptom_entries,
        "symptom_types": all_symptom_types,
        "selected_symptoms": selected_symptoms,
        "calendar": cal,
        "month": month,
        "year": year,
        "selected_day": selected_day,
        "selected_date": selected_date.strftime("%Y-%m-%d"),
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    }

    return render(request, "allergy/partials/symptoms/container_allergy_symptoms.html", context)


@require_GET
def partial_symptom_add(request: HttpRequest, symptom_uuid: str) -> HttpResponse:
    user = cast(User, request.user)
    symptom_type = SymptomType.objects.filter(user=user).get(uuid=symptom_uuid)

    return render(request, "allergy/partials/symptoms/intensity/add_selector.html", {"symptom_type": symptom_type})


@require_http_methods(["DELETE"])
def partial_symptom_remove(request: HttpRequest, symptom_uuid: str) -> HttpResponse:
    user = cast(User, request.user)
    symptom = SymptomEntry.objects.filter(symptom_type__uuid=symptom_uuid, user=user).first()
    if symptom:
        symptom.delete()

    symptom_type = SymptomType.objects.filter(uuid=symptom_uuid).first()
    return render(request, "allergy/partials/symptoms/intensity/remove_selector.html", {"symptom_type": symptom_type})


@require_POST
def partial_symptom_save(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    form = AddSymptomForm(request.POST, user=user)
    if not form.is_valid():
        return render(
            request,
            "allergy/partials/symptoms/intensity/select_intensity.html",
            {
                "form": form,
            },
        )

    entry = form.save()
    symptom_type = entry.symptom_type

    return render(
        request,
        "allergy/partials/symptoms/intensity/select_intensity.html",
        {
            "symptom_type": symptom_type,
            "entry": entry,
        },
    )


@require_POST
def partial_symptom_delete(request: HttpRequest) -> HttpResponse:
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
