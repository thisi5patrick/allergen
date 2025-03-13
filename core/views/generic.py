from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from django_htmx.http import HttpResponseClientRedirect, trigger_client_event

from allergy.models import SymptomType
from core.forms import RegistrationForm


def view_404(request: HttpRequest, exception: None | Exception = None) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard_view")
    return redirect("login_view")


@require_GET
@login_not_required
def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard_view")

    return render(request, "login/login.html")


@require_POST
@login_not_required
def login_process(request: HttpRequest) -> HttpResponse:
    username = request.POST.get("username")
    password = request.POST.get("password")
    remember_me = request.POST.get("remember_me") == "on"

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)

        if not remember_me:
            request.session.set_expiry(0)

        return HttpResponseClientRedirect("/dashboard/")
    else:
        error_message = "Invalid username or password. Please try again."
        response = render(request, "login/login_error_message.html", {"error_message": error_message})
        return trigger_client_event(response, "login_error")


@require_GET
@login_not_required
def registration_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard_view")
    return render(request, "registration/registration.html")


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

        return HttpResponseClientRedirect("/dashboard/")

    response = render(request, "registration/registration_error_message.html", {"form": form})
    return trigger_client_event(response, "registration_error")


@require_POST
def logout_process(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logout(request)
    return HttpResponseClientRedirect("/login/")
