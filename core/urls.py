from django.urls import path

from core.views import generic, user_panel

generic_urls = [
    path("login/", generic.login_view, name="login_view"),
    path("login/process/", generic.login_process, name="login_process"),
    path("registration/", generic.registration_view, name="registration_view"),
    path("registration/process/", generic.registration_process, name="registration_process"),
    path("logout/", generic.logout_process, name="logout_process"),
]

user_panel_urls = [
    path("me/overview/", user_panel.overview_view, name="overview_view"),
    path("me/symptoms/", user_panel.symptoms_view, name="symptoms_view"),
    path("me/food-allergies/", user_panel.food_allergies_view, name="food_allergies_view"),
    path("me/medications/", user_panel.medications_view, name="medications_view"),
    path("me/change-password/", user_panel.change_password_view, name="change_password_view"),
    path("me/delete-account/", user_panel.delete_account_view, name="delete_account_view"),
]

urlpatterns = generic_urls + user_panel_urls
