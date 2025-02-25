from django.urls import path

from core import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_page, name="login"),
    path("login/process", views.login_process, name="login_process"),
]
