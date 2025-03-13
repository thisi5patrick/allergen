from django.urls import path

from core.views import generic, user_panel

generic_urls = [
    path("login/", generic.login_view, name="login_view"),
    path("login/process/", generic.login_process, name="login_process"),
    path("registration/", generic.registration_view, name="registration_view"),
    path("registration/process/", generic.registration_process, name="registration_process"),
    path("logout/", generic.logout_process, name="logout_process"),
]

overview_urls = [
    path("me/overview/", user_panel.overview_view, name="overview_view"),
]

symptoms_urls = [
    path("me/symptoms/", user_panel.symptoms_view, name="symptoms_view"),
    path("me/symptoms/symptoms_list/", user_panel.symptoms_list_partial, name="symptoms_list_partial"),
    path("me/symptoms/add_symptom/", user_panel.add_new_symptom_partial, name="add_new_symptom_partial"),
    path(
        "me/symptoms/add_symptom/process/",
        user_panel.process_add_new_symptom_partial,
        name="process_add_new_symptom_partial",
    ),
]

food_allergy_urls = [
    path("me/food-allergies/", user_panel.food_allergies_view, name="food_allergies_view"),
]

medications_urls = [
    path("me/medications/", user_panel.medications_view, name="medications_view"),
]

user_panel_urls = (
    [  # noqa: RUF005
        path("me/change-password/", user_panel.change_password_view, name="change_password_view"),
        path("me/delete-account/", user_panel.delete_account_view, name="delete_account_view"),
    ]
    + overview_urls
    + symptoms_urls
    + food_allergy_urls
    + medications_urls
)

urlpatterns = generic_urls + user_panel_urls
