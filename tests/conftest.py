import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture()
def user() -> User:
    return User.objects.create_user(username="testuser", password="testpassword")


@pytest.fixture()
def authenticated_client(user: User) -> Client:
    client = Client()
    client.login(username="testuser", password="testpassword")

    return client


@pytest.fixture()
def anonymous_client() -> Client:
    return Client()
