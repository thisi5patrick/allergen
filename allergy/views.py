from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect


def redirect_to_dashboard(request: HttpRequest) -> HttpResponse:
    return redirect("dashboard")

def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "allergy/dashboard.html")
