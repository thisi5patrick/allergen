from django.urls import path

from settings.views import account, food_allergies, medications, overview, symptoms

overview_urls = [
    path("overview/", overview.overview_tab, name="overview_tab"),
]

symptoms_urls = [
    path("symptoms/", symptoms.symptoms_tab, name="symptoms_tab"),
    path("symptoms/list/", symptoms.partial_existing_symptoms, name="partial_existing_symptoms"),
    path(
        "symptoms/new_symptom/save/",
        symptoms.partial_new_symptom_type_save,
        name="partial_new_symptom_type_save",
    ),
    path(
        "symptoms/remove/<uuid:symptom_type_uuid>/",
        symptoms.partial_symptom_remove,
        name="partial_symptom_type_remove",
    ),
]

food_allergy_urls = [
    path("food-allergies/", food_allergies.food_allergies_tab, name="food_allergies_tab"),
]

medications_urls = [
    path("medications/", medications.medications_tab, name="medications_tab"),
    path("medications/save/", medications.add_medication, name="add_medication"),
    path("medications/<uuid:medication_uuid>/", medications.delete_medication, name="delete_medication"),
]

account_urls = [
    path("change-password/", account.change_password_tab, name="change_password_tab"),
    path("delete-account/", account.delete_account_tab, name="delete_account_tab"),
]


urlpatterns = overview_urls + symptoms_urls + food_allergy_urls + medications_urls + account_urls

app_name = "settings"
