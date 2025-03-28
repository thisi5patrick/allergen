from typing import cast

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

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
def partial_existing_symptoms(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    symptom_types = (
        SymptomType.objects.filter(user=user)
        .select_related("symptom_entries")
        .values("uuid", "name")
        .annotate(entries_count=Count("symptom_entries"))
        .order_by("name")
        .all()
    )

    return render(
        request,
        "settings/tabs/partials/symptoms/existing_symptoms.html",
        {
            "symptom_types": symptom_types,
        },
    )


@require_POST
def partial_new_symptom_type_save(request: HttpRequest) -> HttpResponse:
    form = AddNewSymptomForm(request.POST, user=request.user)
    symptom_type = None
    if form.is_valid():
        symptom_type = form.save()
    return render(
        request,
        "settings/tabs/partials/symptoms/add_symptom_type.html",
        {
            "form": form,
            "symptom_type": symptom_type,
        },
    )


@require_http_methods(["DELETE"])
def partial_symptom_remove(request: HttpRequest, symptom_type_uuid: str) -> HttpResponse:
    user = cast(User, request.user)

    symptom = SymptomType.objects.filter(uuid=symptom_type_uuid, user=user).first()
    if symptom:
        symptom.delete()

    return HttpResponse(status=200)
