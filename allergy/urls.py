from django.urls import path

from allergy import views

urlpatterns = [
    path("", views.redirect_to_dashboard, name="index"),
    path("dashboard/", views.dashboard_view, name="dashboard_view"),
    path("calendar/<int:year>/<int:month>/<int:day>/", views.get_calendar_partial, name="get_calendar_partial"),
    path("add_symptom/", views.add_symptom_partial, name="add_symptom_partial"),
    path("delete_symptom/", views.delete_symptom_partial, name="delete_symptom_partial"),
]
