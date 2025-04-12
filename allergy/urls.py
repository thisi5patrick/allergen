from django.urls import path, re_path

from allergy import views

urlpatterns = [
    path("", views.redirect_to_dashboard, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    re_path(
        r"^partial/calendar/(?P<year>\d{4})/(?P<month>\d{1,2})(?:/(?P<day>\d{1,2}))?/$",
        views.partial_calendar,
        name="partial_calendar",
    ),
    path(
        "symptoms/<int:year>/<int:month>/<int:day>/",
        views.partial_symptoms_container,
        name="partial_symptoms_container",
    ),
    path("symptom/add/<uuid:symptom_uuid>/", views.partial_symptom_add, name="partial_symptom_add"),
    path("symptom/remove/<uuid:symptom_uuid>/", views.partial_symptom_remove, name="partial_symptom_remove"),
    path("symptom/save/", views.partial_symptom_save, name="partial_symptom_save"),
]

app_name = "allergy"
