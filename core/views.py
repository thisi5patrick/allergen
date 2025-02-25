from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from django_htmx.http import HttpResponseClientRedirect, trigger_client_event


@login_required(redirect_field_name=None, login_url="login")
def index(request: HttpRequest) -> HttpResponse:
    return redirect("dashboard")


@require_GET
def login_page(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")

    return render(request, "login/login.html")


@require_POST
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
