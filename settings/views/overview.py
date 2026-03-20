from typing import cast

from django.contrib.auth.models import User
from django.db.models import Avg, Count, Max
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from allergy.models import SymptomEntry
from settings.views.enums import ActiveTab


@require_GET
def overview_tab(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)

    entries = SymptomEntry.objects.filter(user=user)

    days_with_symptoms = entries.values("entry_date").distinct().count()
    total_entries = entries.count()
    recent_symptoms = entries.select_related("symptom_type").order_by(
        "-entry_date", "-created_at", "symptom_type__name"
    )[:5]
    top_symptoms = (
        entries.values("symptom_type", "symptom_type__name")
        .annotate(count=Count("symptom_type"))
        .order_by("-count", "symptom_type__name")[:5]
    )
    average_intensity = entries.aggregate(avg_intensity=Avg("intensity"))["avg_intensity"]
    latest_entry_date = entries.aggregate(latest_entry_date=Max("entry_date"))["latest_entry_date"]

    context = {
        "active_tab": ActiveTab.OVERVIEW,
        "days_with_symptoms": days_with_symptoms,
        "total_entries": total_entries,
        "recent_symptoms": recent_symptoms,
        "top_symptoms": top_symptoms,
        "average_intensity": round(average_intensity, 1) if average_intensity is not None else None,
        "latest_entry_date": latest_entry_date,
    }
    return render(request, "settings/tabs/overview.html", context)
