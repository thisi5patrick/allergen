from django.urls import path

from settings import views

overview_urls = [
    path("overview/", views.overview_view, name="overview_view"),
]

symptoms_urls = [
    path("symptoms/", views.symptoms_view, name="symptoms_view"),
    path("symptoms/symptoms_list/", views.symptoms_list_partial, name="symptoms_list_partial"),
    path("symptoms/add_symptom/", views.add_new_symptom_partial, name="add_new_symptom_partial"),
    path(
        "symptoms/add_symptom/process/",
        views.process_add_new_symptom_partial,
        name="process_add_new_symptom_partial",
    ),
]

food_allergy_urls = [
    path("food-allergies/", views.food_allergies_view, name="food_allergies_view"),
]

medications_urls = [
    path("medications/", views.medications_view, name="medications_view"),
]

views_urls = (
    [  # noqa: RUF005
        path("change-password/", views.change_password_view, name="change_password_view"),
        path("delete-account/", views.delete_account_view, name="delete_account_view"),
    ]
    + overview_urls
    + symptoms_urls
    + food_allergy_urls
    + medications_urls
)

urlpatterns = views_urls
