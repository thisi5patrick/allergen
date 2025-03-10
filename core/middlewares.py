# mypy: ignore-errors
from django.contrib.auth.middleware import LoginRequiredMiddleware


class CustomLoginRequiredMiddleware(LoginRequiredMiddleware):
    redirect_field_name = None
