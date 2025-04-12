import calendar
from datetime import date, timedelta
from typing import cast

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from allergy.forms import AddSymptomForm
from allergy.models import SymptomEntry, SymptomType


def redirect_to_dashboard(request: HttpRequest) -> HttpResponse:
    dashboard_redirect = reverse("allergy:dashboard")
    return redirect(dashboard_redirect)


@require_GET
def dashboard(request: HttpRequest) -> HttpResponse:
    today = date.today()
    context = {
        "current_year": today.year,
        "current_month": today.month,
        "current_day": today.day,
    }
    return render(request, "allergy/dashboard.html", context)


@require_GET
def partial_calendar(request: HttpRequest, year: str, month: str, day: str | None = None) -> HttpResponse:
    try:
        year_int = int(year)
        month_int = int(month)
        day_int = int(day) if day is not None else None

        target_day_for_validation = day_int if day_int else 1
        target_date = date(year_int, month_int, target_day_for_validation)

        year_int = target_date.year
        month_int = target_date.month

    except (ValueError, TypeError):
        return HttpResponseBadRequest("Invalid date parameters provided.")

    cal_matrix = calendar.monthcalendar(year_int, month_int)
    month_name = calendar.month_name[month_int]

    prev_month_date = date(year_int, month_int, 1) - timedelta(days=1)
    prev_month = prev_month_date.month
    prev_year = prev_month_date.year

    last_day_of_month = calendar.monthrange(year_int, month_int)[1]
    next_month_date = date(year_int, month_int, last_day_of_month) + timedelta(days=1)
    next_month = next_month_date.month
    next_year = next_month_date.year

    selected_day = day_int
    selected_date_str = None
    if selected_day:
        selected_date_str = date(year_int, month_int, selected_day).strftime("%Y-%m-%d")

    context = {
        "calendar_matrix": cal_matrix,
        "current_month_num": month_int,
        "current_month_name": month_name,
        "current_year": year_int,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "selected_day": selected_day,
        "selected_date_str": selected_date_str,
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
