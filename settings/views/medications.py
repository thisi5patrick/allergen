import uuid
from typing import cast

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from allergy.forms import MedicationForm
from allergy.models import Medication
from settings.views.enums import ActiveTab


@require_GET
def medications_tab(request: HttpRequest) -> HttpResponse:
    context = {
        "active_tab": ActiveTab.MEDICATIONS,
    }
    return render(request, "settings/tabs/medications.html", context)


@require_GET
def partial_existing_medications(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    medications = Medication.objects.filter(user=user).order_by("medication_name")

    context = {"medications": medications}
    return render(request, "settings/tabs/partials/medications/existing_medications.html", context)


@require_GET
def partial_new_medication_form(request: HttpRequest) -> HttpResponse:
    form = MedicationForm()

    context = {"form": form}
    return render(request, "settings/tabs/partials/medications/add_medication_form.html", context)


@require_POST
def partial_new_medication_save(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    form = MedicationForm(request.POST, user=user)

    if form.is_valid():
        medication = form.save()
        new_form = MedicationForm()
        context = {
            "medication": medication,
            "form": new_form,
        }
        return render(request, "settings/tabs/partials/medications/add_medication.html", context)

    context = {"form": form}
    return render(request, "settings/tabs/partials/medications/add_medication_form.html", context)


@require_http_methods(["DELETE"])
def partial_delete_medication(request: HttpRequest, medication_uuid: uuid.UUID) -> HttpResponse:
    user = cast(User, request.user)

    medication = Medication.objects.filter(uuid=medication_uuid, user=user).filter()
    if not medication:
        return HttpResponseBadRequest("Invalid medication parameter provided.")

    medication.delete()

    return HttpResponse(status=200)
