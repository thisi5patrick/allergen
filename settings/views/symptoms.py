from typing import cast

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from allergy.models import SymptomType
from settings.forms.new_symptom import AddNewSymptomForm
from settings.views.enums import ActiveTab


@require_GET
def symptoms_tab(request: HttpRequest) -> HttpResponse:
    context = {
        "active_tab": ActiveTab.SYMPTOMS,
    }
    return render(request, "settings/tabs/symptoms.html", context)


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

    return render(
        request,
        "settings/tabs/partials/symptoms_list.html",
        {
            "symptom_types": symptom_types,
        },
    )


@require_GET
def add_new_symptom_partial(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "settings/tabs/partials/add_new_symptom.html",
        {},
    )


@require_POST
def process_add_new_symptom_partial(request: HttpRequest) -> HttpResponse:
    form = AddNewSymptomForm(request.POST, user=request.user)
    if form.is_valid():
        form.save()
    return render(
        request,
        "settings/tabs/partials/add_new_symptom.html",
        {
            "form": form,
        },
    )
