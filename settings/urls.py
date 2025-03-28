from django.urls import path

from settings.views import account, food_allergies, medications, overview, symptoms

overview_urls = [
    path("overview/", overview.overview_tab, name="overview_tab"),
]

symptoms_urls = [
    path("symptoms/", symptoms.symptoms_tab, name="symptoms_tab"),
    path("symptoms/symptoms_list/", symptoms.symptoms_list_partial, name="symptoms_list_partial"),
    path("symptoms/add_symptom/", symptoms.add_new_symptom_partial, name="add_new_symptom_partial"),
    path(
        "symptoms/add_symptom/process/",
        symptoms.process_add_new_symptom_partial,
        name="process_add_new_symptom_partial",
    ),
]

food_allergy_urls = [
    path("food-allergies/", food_allergies.food_allergies_tab, name="food_allergies_tab"),
]

medications_urls = [
    path("medications/", medications.medications_tab, name="medications_tab"),
]

account_urls = [
    path("change-password/", account.change_password_tab, name="change_password_tab"),
    path("delete-account/", account.delete_account_tab, name="delete_account_tab"),
]


urlpatterns = overview_urls + symptoms_urls + food_allergy_urls + medications_urls + account_urls
