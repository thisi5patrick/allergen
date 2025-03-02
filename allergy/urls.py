from django.urls import path

from allergy import views

urlpatterns = [
    path("", views.redirect_to_dashboard, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("calendar/<int:year>/<int:month>/<int:day>/", views.get_calendar, name="calendar"),
    path("add_symptom/", views.add_symptom, name="add_symptom"),
    path("delete_symptom/", views.delete_symptom, name="delete_symptom"),
]
