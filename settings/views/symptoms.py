import uuid
from typing import cast

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
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
        .values("uuid", "name")
        .annotate(entries_count=Count("symptom_entries"))
        .order_by("name")
    )

    return render(
        request,
        "settings/tabs/partials/symptoms/existing_symptoms.html",
        {
            "symptom_types": symptom_types,
        },
    )


@require_GET
def partial_new_symptom_type_form(request: HttpRequest) -> HttpResponse:
    form = AddNewSymptomForm()
    return render(request, "settings/tabs/partials/symptoms/add_symptom_type.html", {"form": form})


@require_POST
def partial_new_symptom_type_save(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    form = AddNewSymptomForm(request.POST, user=user)

    if form.is_valid():
        symptom_type = form.save()
        new_empty_form = AddNewSymptomForm()
        context = {
            "symptom_type": symptom_type,
            "form": new_empty_form,
        }
        response = render(request, "settings/tabs/partials/symptoms/add_symptom_type_oob.html", context)
        return response

    return render(
        request,
        "settings/tabs/partials/symptoms/add_symptom_type.html",
        context={
            "form": form,
            "symptom_type": None,
        },
    )


@require_http_methods(["DELETE"])
def partial_symptom_remove(request: HttpRequest, symptom_type_uuid: uuid.UUID) -> HttpResponse:
    user = cast(User, request.user)

    symptom = SymptomType.objects.filter(uuid=symptom_type_uuid, user=user).first()
    if not symptom:
        return HttpResponseBadRequest("Invalid symptom type parameter provided.")

    symptom.delete()

    return HttpResponse(status=200)
