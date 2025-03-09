from django.urls import path

from core.views import generic, user_panel

generic_urls = [
    path("login/", generic.login_page, name="login"),
    path("login/process/", generic.login_process, name="login_process"),
    path("registration/", generic.registration_page, name="registration"),
    path("registration/process/", generic.registration_process, name="register_process"),
    path("logout/", generic.logout_process, name="logout"),
]

user_panel_urls = [
    path("me/overview/", user_panel.user_overview, name="user_overview"),
    path("me/symptoms/", user_panel.user_symptoms, name="user_symptoms"),
    path("me/food-allergies/", user_panel.user_food_allergies, name="user_food_allergies"),
    path("me/medications/", user_panel.user_medications, name="user_medications"),
    path("me/change-password/", user_panel.change_password, name="change_password"),
    path("me/delete-account/", user_panel.delete_account, name="delete_account"),
]

urlpatterns = generic_urls + user_panel_urls
