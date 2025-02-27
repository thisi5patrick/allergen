from django.urls import path

from core import views

urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("login/process/", views.login_process, name="login_process"),
    path("registration/", views.registration_page, name="registration"),
    path("registration/process/", views.registration_process, name="register_process"),
]
