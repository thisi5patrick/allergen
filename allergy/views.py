import calendar
import uuid
from datetime import date, timedelta
from typing import cast

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from allergy.forms import AddSymptomForm
from allergy.models import SymptomEntry, SymptomType


def _get_days_with_entries(user: User, year: int, month: int) -> list[int]:
    return list(
        SymptomEntry.objects.filter(user=user, entry_date__year=year, entry_date__month=month)
        .values_list("entry_date__day", flat=True)
        .distinct()
    )


def _get_explicit_selected_date(request: HttpRequest) -> date | None:
    selected_date_str = request.GET.get("selected_date")
    if not selected_date_str:
        return None
    try:
        return date.fromisoformat(selected_date_str)
    except ValueError:
        return None


def _build_calendar_context(
    user: User,
    year: int,
    month: int,
    explicit_selected_date: date | None,
    *,
    fallback_selected_date: date | None,
) -> dict[str, object]:
    cal_matrix = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    days_with_entries = _get_days_with_entries(user, year, month)

    prev_month_date = date(year, month, 1) - timedelta(days=1)
    prev_month = prev_month_date.month
    prev_year = prev_month_date.year
    last_day_of_month = calendar.monthrange(year, month)[1]
    next_month_date = date(year, month, last_day_of_month) + timedelta(days=1)
    next_month = next_month_date.month
    next_year = next_month_date.year

    selected_day = None
    if explicit_selected_date and explicit_selected_date.year == year and explicit_selected_date.month == month:
        selected_day = explicit_selected_date.day
    elif fallback_selected_date and fallback_selected_date.year == year and fallback_selected_date.month == month:
        selected_day = fallback_selected_date.day

    selected_date_str = None
    if selected_day is not None:
        selected_date_str = date(year, month, selected_day).strftime("%Y-%m-%d")

    explicit_selected_date_str = explicit_selected_date.isoformat() if explicit_selected_date else None

    return {
        "calendar_matrix": cal_matrix,
        "current_month_num": month,
        "current_month_name": month_name,
        "current_year": year,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "explicit_selected_date_str": explicit_selected_date_str,
        "selected_day": selected_day,
        "selected_date_str": selected_date_str,
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "days_with_entries": days_with_entries,
    }


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

    except ValueError, TypeError:
        return HttpResponseBadRequest("Invalid date parameters provided.")

    user = cast(User, request.user)
    explicit_selected_date = _get_explicit_selected_date(request)
    if day_int is not None:
        explicit_selected_date = date(year_int, month_int, day_int)

    context = _build_calendar_context(
        user,
        year_int,
        month_int,
        explicit_selected_date,
        fallback_selected_date=date.today() if explicit_selected_date is None else None,
    )

    return render(request, "allergy/partials/calendar/calendar.html", context)


@require_GET
def symptoms_container_partial(request: HttpRequest, year: int, month: int, day: int) -> HttpResponse:
    try:
        selected_date = date(year, month, day)
    except ValueError:
        return HttpResponseBadRequest("Invalid date parameters provided.")

    user = cast(User, request.user)

    symptom_entries = (
        SymptomEntry.objects.filter(user=user, entry_date=selected_date)
        .select_related("symptom_type")
        .order_by("symptom_type__name")
    )
    all_symptom_types = SymptomType.objects.filter(user=user).order_by("name")

    selected_symptoms_map = {entry.symptom_type: entry for entry in symptom_entries}

    context = {
        "symptom_entries": symptom_entries,
        "symptom_types": all_symptom_types,
        "selected_symptoms_map": selected_symptoms_map,
        "selected_date": selected_date,
        "selected_date_str": selected_date.strftime("%Y-%m-%d"),
        "current_year": year,
        "current_month_num": month,
        "selected_day": day,
    }
    context.update(
        _build_calendar_context(
            user,
            year,
            month,
            selected_date,
            fallback_selected_date=None,
        )
    )

    return render(request, "allergy/partials/symptoms/symptoms_container.html", context)


@require_GET
def symptom_add_partial(request: HttpRequest, symptom_uuid: str) -> HttpResponse:
    user = cast(User, request.user)

    symptom_type = SymptomType.objects.filter(user=user, uuid=symptom_uuid).first()
    if not symptom_type:
        return HttpResponseBadRequest("Invalid or unknown symptom specified.")

    selected_date_str = request.GET.get("selected_date")
    selected_date_obj = None
    if selected_date_str:
        try:
            selected_date_obj = date.fromisoformat(selected_date_str)
        except ValueError:
            pass

    context = {
        "symptom_type": symptom_type,
        "selected_date": selected_date_obj,
        "selected_date_str": selected_date_str,
    }

    return render(request, "allergy/partials/symptoms/intensity/add_selector.html", context)


@require_http_methods(["DELETE"])
def symptom_remove_partial(
    request: HttpRequest, year: int, month: int, day: int, symptom_uuid: uuid.UUID
) -> HttpResponse:
    try:
        selected_date = date(year, month, day)
    except ValueError:
        return HttpResponseBadRequest("Invalid date parameters provided.")

    user = cast(User, request.user)

    symptom_type = SymptomType.objects.filter(user=user, uuid=symptom_uuid).first()
    if not symptom_type:
        return HttpResponseBadRequest("Invalid or unknown symptom specified for removal.")

    _deleted_count, _ = SymptomEntry.objects.filter(
        user=user, entry_date=selected_date, symptom_type=symptom_type
    ).delete()

    context = {
        "symptom_type": symptom_type,
        "selected_date": selected_date,
        "selected_date_str": selected_date.strftime("%Y-%m-%d"),
    }

    return render(request, "allergy/partials/symptoms/intensity/remove_selector.html", context)


@require_POST
def symptom_save_partial(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    form = AddSymptomForm(request.POST, user=user)

    symptom_type: SymptomType | None

    if form.is_valid():
        entry = form.save()
        symptom_type = entry.symptom_type

        context = {
            "symptom_type": symptom_type,
            "entry": entry,
            "selected_date_str": entry.entry_date.strftime("%Y-%m-%d"),
        }
        return render(request, "allergy/partials/symptoms/intensity/select_intensity.html", context)

    symptom_type = None
    symptom_uuid_str = request.POST.get("symptom_uuid")
    if symptom_uuid_str:
        try:
            symptom_type = SymptomType.objects.filter(user=user, uuid=symptom_uuid_str).first()
        except ValueError, ValidationError:
            pass

    context = {"form": form, "symptom_type": symptom_type, "selected_date_str": request.POST.get("selected_date")}

    return render(request, "allergy/partials/symptoms/intensity/select_intensity.html", context)
