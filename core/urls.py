from django.urls import path

from core import views

urlpatterns = [
    path("login/", views.login_view, name="login_view"),
    path("login/process/", views.login_process, name="login_process"),
    path("registration/", views.registration_view, name="registration_view"),
    path("registration/process/", views.registration_process, name="registration_process"),
    path("logout/", views.logout_process, name="logout_process"),
]
