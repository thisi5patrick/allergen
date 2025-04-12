import pytest
from django.contrib.auth.models import User
from django.test import Client

from tests.factories.user import UserFactory

TEST_USERNAME_1 = "testuser_1"
TEST_PASSWORD_1 = "testpassword_1"

TEST_USERNAME_2 = "testuser_2"
TEST_PASSWORD_2 = "testpassword_2"


@pytest.fixture
def user() -> User:
    user = UserFactory.create(username=TEST_USERNAME_1)
    user.set_password(TEST_PASSWORD_1)
    user.save()

    return user


@pytest.fixture
def second_user() -> User:
    user = UserFactory.create(username=TEST_USERNAME_2)
    user.set_password(TEST_PASSWORD_2)
    user.save()

    return user


@pytest.fixture
def authenticated_client(user: User) -> Client:
    client = Client()
    client.login(username=TEST_USERNAME_1, password=TEST_PASSWORD_1)

    return client


@pytest.fixture
def authenticated_second_user_client(second_user: User) -> Client:
    client = Client()
    client.login(username=TEST_USERNAME_2, password=TEST_PASSWORD_2)

    return client


@pytest.fixture
def anonymous_client() -> Client:
    return Client()
