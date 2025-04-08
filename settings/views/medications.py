from typing import cast

from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from allergy.forms import MedicationForm
from allergy.models import Medications
from settings.views.enums import ActiveTab


@require_GET
def medications_tab(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    medications = Medications.objects.filter(user=user).order_by("medication_name")
    form = MedicationForm()

    return render(
        request,
        "settings/tabs/medications.html",
        {
            "active_tab": ActiveTab.MEDICATIONS,
            "medications": medications,
            "form": form,
        },
    )


@require_POST
def add_medication(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    form = MedicationForm(request.POST, user=user)
    if form.is_valid():
        medication = form.save()

        return render(
            request,
            "settings/tabs/partials/medications/new_medication_success.html",
            {"medication": medication, "form": MedicationForm()},
        )

    return render(
        request,
        "settings/tabs/partials/medications/new_medication_form.html",
        {
            "form": form,
        },
    )


@require_http_methods(["DELETE"])
def delete_medication(request: HttpRequest, medication_uuid: str) -> HttpResponse:
    user = cast(User, request.user)
    medication = Medications.objects.filter(uuid=medication_uuid, user=user).filter()
    if medication:
        medication.delete()

    return HttpResponse(status=200)
