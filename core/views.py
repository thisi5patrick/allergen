from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from allergy.models import SymptomType
from core.forms.login import LoginForm
from core.forms.registration import RegistrationForm


def view_404(request: HttpRequest, exception: None | Exception = None) -> HttpResponse:
    if request.user.is_authenticated:
        dashboard_redirect = reverse("dashboard")
        return redirect(dashboard_redirect)
    login_redirect = reverse("login_view")
    return redirect(login_redirect)


@require_GET
@login_not_required
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        dashboard_redirect = reverse("dashboard")
        return redirect(dashboard_redirect)

    form = LoginForm()
    return render(request, "login/login.html", {"form": form})


@require_POST
@login_not_required
def login_process(request: HttpRequest) -> HttpResponse:
    form = LoginForm(request.POST)

    if form.is_valid():
        user = form.cleaned_data["user"]

        if form.cleaned_data.get("remember_me"):
            request.session.set_expiry(60 * 60 * 24 * 7)
        else:
            request.session.set_expiry(None)

        login(request, user)
        dashboard_redirect = reverse("dashboard")
        return redirect(dashboard_redirect)

    return render(request, "login/login_form_partial.html", {"form": form})


@require_GET
@login_not_required
def registration_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        dashboard_redirect = reverse("dashboard")
        return redirect(dashboard_redirect)

    form = RegistrationForm()
    return render(request, "registration/registration.html", {"form": form})


@require_POST
@login_not_required
def registration_process(request: HttpRequest) -> HttpResponse:
    form = RegistrationForm(request.POST)

    if form.is_valid():
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )
        user.save()

        SymptomType.objects.bulk_create(
            [
                SymptomType(user=user, name="Sneezing"),
                SymptomType(user=user, name="Runny nose"),
                SymptomType(user=user, name="Itchy eyes"),
                SymptomType(user=user, name="Headache"),
            ]
        )

        login(request, user)

        dashboard_redirect = reverse("dashboard")
        return redirect(dashboard_redirect)

    return render(request, "registration/registration_form_partial.html", {"form": form})


@require_POST
def logout_process(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logout(request)
    login_redirect = reverse("login_view")
    return redirect(login_redirect)
