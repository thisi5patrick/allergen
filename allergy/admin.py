from django.contrib import admin

from allergy.models import SymptomEntry, SymptomType


@admin.register(SymptomType)
class SymptomTypeAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "user")


@admin.register(SymptomEntry)
class SymptomEntryAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("user", "entry_date", "symptom_type", "intensity")
