import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.test import Client

User = get_user_model()

TEST_USERNAME = "testuser"
TEST_PASSWORD = "testpassword"


@pytest.fixture()
def user() -> AbstractUser:
    return User.objects.create_user(username=TEST_USERNAME, password=TEST_PASSWORD)


@pytest.fixture()
def authenticated_client(user: AbstractUser) -> Client:
    client = Client()
    client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

    return client


@pytest.fixture()
def anonymous_client() -> Client:
    return Client()
