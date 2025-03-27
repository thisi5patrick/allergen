from enum import StrEnum
from typing import cast

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from django_htmx.http import trigger_client_event

from allergy.models import SymptomEntry, SymptomType
from settings.forms.new_symptom import AddNewSymptomForm


class ActiveTab(StrEnum):
    OVERVIEW = "overview"
    SYMPTOMS = "symptoms"
    FOOD_ALLERGIES = "food_allergies"
    MEDICATIONS = "medications"
    CHANGE_PASSWORD = "change_password"
    DELETE_ACCOUNT = "delete_account"


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
        "active_tab": ActiveTab.OVERVIEW,
        "days_with_symptoms": days_with_symptoms,
        "total_entries": total_entries,
        "recent_symptoms": recent_symptoms,
        "top_symptoms": top_symptoms,
    }
    return render(request, "user/tabs/user_overview.html", context)


@require_GET
def symptoms_view(request: HttpRequest) -> HttpResponse:
    context = {
        "active_tab": ActiveTab.SYMPTOMS,
    }
    return render(request, "user/tabs/user_symptoms.html", context)


@require_GET
def symptoms_list_partial(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    symptom_types = (
        SymptomType.objects.filter(user=user)
        .select_related("symptom_entries")
        .values("name")
        .annotate(entries_count=Count("symptom_entries"))
        .order_by("name")
        .all()
    )

    response = render(
        request,
        "user/tabs/partials/symptoms_list.html",
        {
            "symptom_types": symptom_types,
        },
    )
    return trigger_client_event(response, name="symptoms_list_partial")


@require_GET
def add_new_symptom_partial(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "user/tabs/partials/add_new_symptom.html",
        {},
    )


@require_POST
def process_add_new_symptom_partial(request: HttpRequest) -> HttpResponse:
    form = AddNewSymptomForm(request.POST, user=request.user)
    if form.is_valid():
        form.save()
    return render(
        request,
        "user/tabs/partials/add_new_symptom.html",
        {
            "form": form,
        },
    )


@require_GET
def food_allergies_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": ActiveTab.FOOD_ALLERGIES})


@require_GET
def medications_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": ActiveTab.MEDICATIONS})


@require_GET
def change_password_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": ActiveTab.CHANGE_PASSWORD})


@require_GET
def delete_account_view(request: HttpRequest) -> HttpResponse:
    return render(request, "user/tabs/user_overview.html", {"active_tab": ActiveTab.DELETE_ACCOUNT})
