from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from settings.views.enums import ActiveTab


@require_GET
def medications_tab(request: HttpRequest) -> HttpResponse:
    return render(request, "settings/tabs/overview.html", {"active_tab": ActiveTab.MEDICATIONS})
