from urllib.parse import parse_qs, urlparse

import pytest
from django.core import mail
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.accounts.permissions import IsCustomer, IsMarketplaceAdmin, IsSeller

pytestmark = pytest.mark.django_db

PASSWORD = "ClearPass!9031"
NEW_PASSWORD = "UpdatedPass!9031"


def register(client: APIClient, email: str = "customer@example.com"):
    return client.post(
        "/api/v1/auth/register/",
        {
            "email": email,
            "password": PASSWORD,
            "password_confirmation": PASSWORD,
            "first_name": "Ava",
            "last_name": "Customer",
        },
        format="json",
    )


def login(client: APIClient, email: str = "customer@example.com", password: str = PASSWORD):
    return client.post("/api/v1/auth/login/", {"email": email, "password": password}, format="json")


def authenticate(client: APIClient, access: str) -> None:
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


def test_customer_can_register_login_and_manage_profile():
    client = APIClient()
    registration = register(client)

    assert registration.status_code == 201
    assert registration.data["email"] == "customer@example.com"
    assert registration.data["role"] == User.Role.CUSTOMER

    login_response = login(client)
    assert login_response.status_code == 200
    assert {"access", "refresh", "user"} <= set(login_response.data)

    authenticate(client, login_response.data["access"])
    profile = client.get("/api/v1/auth/me/")
    assert profile.status_code == 200
    assert profile.data["first_name"] == "Ava"

    update = client.patch("/api/v1/auth/me/", {"last_name": "Updated"}, format="json")
    assert update.status_code == 200
    assert update.data["last_name"] == "Updated"


def test_refresh_rotates_token_and_logout_blacklists_it():
    client = APIClient()
    register(client)
    initial_login = login(client).data

    refreshed = client.post(
        "/api/v1/auth/refresh/", {"refresh": initial_login["refresh"]}, format="json"
    )
    assert refreshed.status_code == 200
    assert refreshed.data["refresh"] != initial_login["refresh"]

    authenticate(client, refreshed.data["access"])
    logout = client.post(
        "/api/v1/auth/logout/", {"refresh": refreshed.data["refresh"]}, format="json"
    )
    assert logout.status_code == 204

    retry = client.post(
        "/api/v1/auth/refresh/", {"refresh": refreshed.data["refresh"]}, format="json"
    )
    assert retry.status_code == 401


def test_password_change_invalidates_existing_access_and_refresh_tokens():
    client = APIClient()
    register(client)
    tokens = login(client).data
    authenticate(client, tokens["access"])

    response = client.post(
        "/api/v1/auth/password/change/",
        {
            "current_password": PASSWORD,
            "new_password": NEW_PASSWORD,
            "new_password_confirmation": NEW_PASSWORD,
        },
        format="json",
    )
    assert response.status_code == 204

    assert client.get("/api/v1/auth/me/").status_code == 401
    assert (
        client.post(
            "/api/v1/auth/refresh/", {"refresh": tokens["refresh"]}, format="json"
        ).status_code
        == 401
    )
    assert login(client, password=NEW_PASSWORD).status_code == 200


def test_password_reset_sends_link_and_sets_new_password():
    client = APIClient()
    register(client)

    response = client.post(
        "/api/v1/auth/password/reset/", {"email": "customer@example.com"}, format="json"
    )
    assert response.status_code == 202
    assert len(mail.outbox) == 1

    query = parse_qs(urlparse(mail.outbox[0].body.split()[-1]).query)
    confirmation = client.post(
        "/api/v1/auth/password/reset/confirm/",
        {
            "uid": query["uid"][0],
            "token": query["token"][0],
            "new_password": NEW_PASSWORD,
            "new_password_confirmation": NEW_PASSWORD,
        },
        format="json",
    )
    assert confirmation.status_code == 204
    assert login(client, password=NEW_PASSWORD).status_code == 200


def test_role_permissions_are_explicit():
    request = type("Request", (), {})()
    request.user = User.objects.create_user(
        email="seller@example.com", password=PASSWORD, role=User.Role.SELLER
    )

    assert IsSeller().has_permission(request, None)
    assert not IsCustomer().has_permission(request, None)
    assert not IsMarketplaceAdmin().has_permission(request, None)
