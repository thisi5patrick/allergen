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
        "partial/symptoms/<int:year>/<int:month>/<int:day>/",
        views.symptoms_container_partial,
        name="symptoms_container_partial",
    ),
    path(
        "partial/symptom/add/<uuid:symptom_uuid>/",
        views.symptom_add_partial,
        name="symptom_add_partial",
    ),
    path(
        "partial/symptom/remove/<int:year>/<int:month>/<int:day>/<uuid:symptom_uuid>/",
        views.symptom_remove_partial,
        name="symptom_remove_partial",
    ),
    path(
        "partial/symptom/save/",
        views.symptom_save_partial,
        name="symptom_save_partial",
    ),
]

app_name = "allergy"
