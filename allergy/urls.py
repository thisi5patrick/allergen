from django.urls import path

from allergy import views

urlpatterns = [
    path("", views.redirect_to_dashboard, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("calendar/<int:year>/<int:month>/<int:day>/", views.partial_calendar, name="partial_calendar"),
    path("calendar/<int:year>/<int:month>/", views.partial_calendar, name="partial_calendar_without_day"),
    path(
        "symptoms/<int:year>/<int:month>/<int:day>/",
        views.partial_symptoms_container,
        name="partial_symptoms_container",
    ),
    path("symptom/add/<uuid:symptom_uuid>/", views.partial_symptom_add, name="partial_symptom_add"),
    path("symptom/remove/<uuid:symptom_uuid>/", views.partial_symptom_remove, name="partial_symptom_remove"),
    path("symptom/save/", views.partial_symptom_save, name="partial_symptom_save"),
    path("symptom/delete/", views.partial_symptom_delete, name="partial_symptom_delete"),
]
